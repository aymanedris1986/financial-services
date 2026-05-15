---
description: Diagnose deployment issues (stale config, connect failures, missing add-in)
---

# Debug a Claude Office deployment

You are helping an enterprise admin diagnose why the deployed add-in isn't
working right. Start by asking **what's wrong**, then route.

## Triage

Ask the admin to describe the symptom. Route by answer:

| Symptom | Section |
|---|---|
| Updated the manifest but users still see old config | [Stale config after update](#stale-config-after-update) |
| Add-in shows "Connection failed" | [Read the error paste](#read-the-error-paste) |
| Add-in doesn't appear in Excel/PowerPoint at all | [Add-in not visible](#add-in-not-visible) |
| Want to test/iterate a manifest locally before deploying | [Sideload a manifest for local debugging](#sideload-a-manifest-for-local-debugging) |
| Sign-in popup fails or loops | [Admin consent](#admin-consent) |
| Need to see the browser console | [Opening browser devtools](#opening-browser-devtools-on-the-add-in) |

If they have an error paste from the add-in (the **Copy error details** button
on the connect-failed screen), always start there. It carries everything.

---

## Read the error paste

Paste structure:

```
Claude for Office connection failed (<Provider>)
Build: <sha>

<friendly message>

Request:
  <key>: <value actually sent>
  ...

Manifest params:
  <key>: <value the deployed manifest carries>
  ...

Raw error:
<SDK/HTTP error>
```

**What to check:**

- `Request:` vs `Manifest params:` delta. Keys are the same snake_case names
  in both blocks, so diff directly. If they differ, the user typed override
  values into the form. If they match, the manifest values went through
  unchanged.
- `Manifest params:` `m` key is the version tag (e.g. `unified-1.0.0.11`). If
  it's below what you last uploaded, the user is on a stale manifest. Go to
  [Stale config](#stale-config-after-update).
- `Raw error:` is the ground truth. Common patterns:
  - `invalid_client` (401, Google) → wrong `google_client_secret` for that
    `google_client_id`. Verify in GCP Console → Credentials.
  - `Load failed (<host>)` → network blocked at the WebView layer. Firewall
    needs to allow that host.
  - `STS AssumeRoleWithWebIdentity failed` → AWS IAM OIDC provider
    misconfigured or role trust policy wrong.
  - `HTTP 401/403` (gateway) → bad token or gateway rejected the key.

---

## Stale config after update

Two caches, two clocks:

| Layer | Who holds it | TTL | How to clear |
|---|---|---|---|
| Service | M365 Admin Center → Exchange Online → client | Up to **72h** for updates (24h for fresh deploys) | Wait, or redeploy with a fresh `<Id>` |
| Client | Office app's Wef folder on each machine | Until app restart, sometimes longer | Clear the cached manifests (see below) |

Microsoft's own FAQ:
> It can take up to 72 hours for add-in updates, changes from turn on or turn off to reflect for users.
> https://learn.microsoft.com/en-us/microsoft-365/admin/manage/centralized-deployment-faq

### Confirm what Admin Center is serving

Admin Center silently ignores re-uploads with the same `<Version>`. If you
uploaded a fix without bumping the fourth segment, it never took. Open M365
Admin Center → Integrated apps → your add-in → check the listed version.

### Force a client-side refresh

Quit Excel/PowerPoint first, then:

This clears the cached add-in manifests **inside** each app's container —
it does not delete the container or any user documents. It removes the
**contents** of the `wef` cache, not the folder itself, with guards so a
missing path is skipped rather than erroring.

> ⚠️ This also removes any **locally sideloaded** manifests in `wef` (see
> [Sideload a manifest](#sideload-a-manifest-for-local-debugging)) — you'll
> need to re-sideload after. If you only want to drop a single sideloaded
> manifest, use the targeted removal in that section instead.

**macOS:**
```bash
for app in Excel Word Powerpoint; do
  base="$HOME/Library/Containers/com.microsoft.$app/Data"
  [ -d "$base/Library/Caches/Microsoft/Office/16.0/Wef" ] && \
    rm -rf "$base/Library/Caches/Microsoft/Office/16.0/Wef"/* && \
    echo "cleared $app Wef cache"
  [ -d "$base/Documents/wef" ] && \
    rm -rf "$base/Documents/wef"/* && \
    echo "cleared $app wef manifests"
done
```

(If the `Library/Caches/.../Wef` path doesn't exist on a given machine, the
guard skips it — older builds keep the cache only under `Documents/wef`.)

**Windows:** delete the contents of the Wef folder, not the folder itself:
```cmd
del /q /s "%LOCALAPPDATA%\Microsoft\Office\16.0\Wef\*" 2>nul
```

Relaunch. If still stale, the service-side cache hasn't caught up. Wait, or
use a fresh `<Id>` (below).

Microsoft's cache-clear doc: https://learn.microsoft.com/en-us/office/dev/add-ins/testing/clear-cache

### Nuclear option: redeploy with a fresh Id

If 72h is unacceptable, a fresh `<Id>` UUID forces Admin Center and every
client to treat it as a brand-new add-in (24h fresh-deploy SLA, usually much
faster). Edit `manifest.xml`, replace the text inside `<Id>` with a new UUID
(`uuidgen` on mac/linux, `[guid]::NewGuid()` in PowerShell), re-upload.

---

## Add-in not visible

- **Not in the ribbon:** Check M365 Admin Center → Integrated apps → your
  add-in → Users tab. Is the user (or their group) assigned? Nested groups
  aren't supported.
- **Shows "My Add-ins" but not the ribbon button:** The manifest's `<Hosts>`
  may not include this app. Check both `<Hosts>` lists (top-level and under
  `<VersionOverrides>`).
- **Fresh deploy, been <24h:** Normal. Microsoft's SLA is 24h for first-time
  deployment visibility.

---

## Sideload a manifest for local debugging

For iterating on a manifest **without going through Admin Center deployment**
(no 24–72h cache wait), point Office at a local manifest file directly. The
manifest stays wherever it is on disk; you just tell Office where to find it.
Pick the recipe for the customer's OS.

### Windows (Wef Developer registry key)

The standard manual sideload — a registry value under the `Wef\Developer`
key whose name is the add-in ID and whose data is the manifest path.

Give the customer this (they replace the path with their own):

```powershell
$manifestPath = (Resolve-Path "C:\path\to\manifest.xml").Path
$addinId = ([xml](Get-Content $manifestPath)).OfficeApp.Id
$wefKey  = "HKCU:\SOFTWARE\Microsoft\Office\16.0\Wef\Developer"
New-Item -Path $wefKey -Force | Out-Null
New-ItemProperty -Path $wefKey -Name $addinId -Value $manifestPath -PropertyType String -Force | Out-Null
```

What this does:
1. Reads the add-in ID from the manifest's `<Id>` element (`OfficeApp.Id`).
2. Creates a `String` value under
   `HKCU:\SOFTWARE\Microsoft\Office\16.0\Wef\Developer` whose **name** is that
   add-in ID and whose **data** is the full path to the manifest file.

Then **fully close and reopen** Excel / Word / PowerPoint — check Task Manager
for lingering processes first (a backgrounded app won't re-read the registry).
The add-in appears on the **Home** tab, or under **Insert → My Add-ins →
Shared Folder**.

To stop sideloading, remove the value (or delete the manifest it points at):

```powershell
Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Office\16.0\Wef\Developer" -Name $addinId
```

### macOS (wef folder)

No registry on macOS — instead drop the manifest into the per-app `wef`
folder. The folder is per-app, so copy into each app you want to test.

Give the customer this (they replace the path with their own):

```bash
MANIFEST="$HOME/path/to/manifest.xml"
NAME="$(basename "$MANIFEST")"
for app in Excel Word Powerpoint; do
  dest="$HOME/Library/Containers/com.microsoft.$app/Data/Documents/wef"
  mkdir -p "$dest"
  cp "$MANIFEST" "$dest/$NAME"
done
```

(`Powerpoint` is the correct container name — lowercase second `p`. Outlook is
`com.microsoft.Outlook`.)

Then **fully quit and reopen** the app — `pkill -f "Microsoft Excel"` (etc.)
to be sure no process lingers, since a backgrounded app won't rescan the
folder. The add-in appears under **Insert → My Add-ins** (look under the
**Developer Add-ins** / shared-folder group), then pin it.

To stop sideloading, delete **only the specific manifest you copied** from
each `wef` folder — do not `rm -rf` the `wef` folder itself (it can hold other
sideloaded add-ins and Office state):

```bash
MANIFEST="$HOME/path/to/manifest.xml"   # same path you sideloaded
NAME="$(basename "$MANIFEST")"
for app in Excel Word Powerpoint; do
  target="$HOME/Library/Containers/com.microsoft.$app/Data/Documents/wef/$NAME"
  [ -f "$target" ] && rm -f "$target" && echo "removed $target"
done
```

**Notes (both platforms):**
- This is per-user and per-machine — it doesn't touch tenant deployment. It's
  purely for the customer to debug/iterate on their own box.
- A locally sideloaded manifest **wins over** a centrally deployed one with
  the same `<Id>`, so this is also a fast way to test a manifest fix before
  re-uploading to Admin Center.
- Pair this with [browser devtools](#opening-browser-devtools-on-the-add-in)
  to see console/network while iterating.
- If a stale copy keeps loading, also clear the cache — see
  [Force a client-side refresh](#force-a-client-side-refresh).

Microsoft's sideloading references:
- Windows: https://learn.microsoft.com/en-us/office/dev/add-ins/testing/create-a-network-shared-folder-catalog-for-task-pane-and-content-add-ins
- macOS: https://learn.microsoft.com/en-us/office/dev/add-ins/testing/sideload-an-office-add-in-on-mac

---

## Admin consent

If the user sees a sign-in popup that closes immediately or loops, the tenant
hasn't granted admin consent to the Claude app. Run
[`:consent`](consent.md) to generate the consent URL for a Global Admin to
approve. The symptom in error pastes: `user_canceled` in the raw error (the
broker maps any unclassifiable close to that).

---

## Silent SSO / Entra token failures

- **`AADSTS50194: …not configured as a multi-tenant application` /
  `Use a tenant-specific endpoint`** — your `graph_client_id` (or the
  `entra_scope` resource app) is a single-tenant app, and the add-in build is
  old enough to still request tokens against the `/common` authority. Newer
  builds resolve a tenant-specific authority automatically when
  `graph_client_id` is set. Fix: have users update to the latest add-in
  version. There is no manifest workaround on an old build.
- **`entra_scope requires graph_client_id`** — `entra_scope` was set without
  `graph_client_id`. Custom-scope access tokens must be issued by your own
  Entra app, not the default; set both. The build script also rejects this
  pairing.
- **Silent SSO fails, then an interactive popup works** — expected on first
  run before a service principal exists in the tenant. Once admin consent is
  granted (see above) the silent path succeeds.

---

## Opening browser devtools on the add-in

When you need the WebView's console — JS errors, network tab, the add-in's
debug logs — you have to attach the host OS's browser devtools. The add-in runs
in an embedded WebView with no address bar and no built-in F12, so each OS
has its own recipe.

### macOS (Safari Web Inspector)

Three gates. **Gate 3 is the one everyone misses.**

1. **Office developer extras** — quit the app first, then:
   ```bash
   defaults write com.microsoft.Excel OfficeWebAddinDeveloperExtras -bool true
   defaults write com.microsoft.Powerpoint OfficeWebAddinDeveloperExtras -bool true
   defaults write com.microsoft.Word OfficeWebAddinDeveloperExtras -bool true
   ```
   Makes right-click → **Inspect Element** appear inside the task pane.

2. **Safari Develop menu** — Safari → Settings → Advanced → check *Show
   features for web developers*.

3. **macOS Developer Tools allowlist** (Sonoma and later) — System Settings
   → Privacy & Security → Developer Tools → toggle **Terminal** on. Without
   this, Safari's Develop menu shows *"No Inspectable Applications"* even
   with gates 1 and 2 open.

With the task pane open, either right-click inside it → **Inspect Element**,
or go to Safari → Develop → *[your machine name]* → find the add-in host
(`pivot.claude.ai` in prod, your configured domain otherwise).

**Gotchas:**
- **Office updates silently reset gate 1.** If inspection worked last week
  and doesn't now, re-run the `defaults write`.
- *"No Inspectable Applications"* = gate 3 missing, or the Office app wasn't
  fully quit before `defaults write`. `pkill -f "Microsoft Excel"` then
  relaunch.
- The task pane has to be **open** (not just the app) for it to appear under
  Safari's Develop menu.

### Windows (Edge DevTools)

Depends on which WebView engine Office is using. Current M365 on Win10/11
with the WebView2 runtime gets Chromium; older perpetual Office or machines
without the runtime may still be on IE11/Trident.

**WebView2 (Chromium — the common case):**

Right-click inside the task pane → **Inspect**. That's it, no gates. If
right-click doesn't show Inspect, install **Microsoft Edge DevTools
Preview** from the Microsoft Store — it lists all attachable WebView2
targets including Office add-ins. Launch it, find the add-in's URL in the
target list, click to attach.

**IE11/Trident (legacy Office 2019/2021 perpetual):**

Run the IEChooser from an admin PowerShell:
```powershell
& "C:\Windows\SysWOW64\F12\IEChooser.exe"
```
Pick the add-in's page from the list. If the list is empty, the task pane
isn't open yet — open it first, then refresh IEChooser.

Microsoft's walkthrough: https://learn.microsoft.com/en-us/office/dev/add-ins/testing/debug-add-ins-using-devtools-edge-chromium
