# TrueSight skin library

This folder supplies optional R15 cosmetic stand models to TrueSight v63+.
The protected main script is separate. It downloads **model data only**; no remote Lua is executed.

## How to import the seven new R15 skins

1. Download `TrueSight_GitHub_Seven_Skins_Import.zip` from the TrueSight ChatGPT conversation.
2. On GitHub, open `skins/import/` and choose **Add file → Upload files**.
3. Upload the ZIP **without extracting it**, renaming it exactly `seven-skins.zip`.
4. Commit the upload to `main`.
5. GitHub Actions → **Import TrueSight R15 skins** should run automatically. If it doesn't, start it with **Run workflow**.

The workflow checks each model's SHA-256 and RBXM header, extracts the seven models into their individual skin folders, commits them, and marks their entries `ready: true` in `skins/manifest.json`.

Until that completes, those skin entries display as **upload pending** and cannot be selected. SPOH remains functional at its existing URL.

## Catalogue format

`manifest.json` contains:
- `id`: lowercase slug, stable between releases
- `name`: text shown in the Skin Source dropdown
- `model`: repo-relative binary .rbxm path
- `ready`: false until the model is uploaded and verified
- `bytes`, `sha256`: verification metadata

The source files for the seven models are not present in GitHub until the ZIP importer has run.
For new skins added later, upload an R15 `model.rbxm` into `skins/<id>/`, add an entry to the manifest and set `ready: true` after validating it.

## Compatibility notes

The R15 rig should contain Humanoid, HumanoidRootPart, UpperTorso, 14+ linked Motor6D joints, and at least one MeshPart. Mesh count no longer needs to match SPOH.
Any embedded particle effects remain in the model. SPOH alone uses its existing dedicated gold aura/barrage VFX and shared-skin marker. Other Github skins are local-only until explicitly supported by the relay.
