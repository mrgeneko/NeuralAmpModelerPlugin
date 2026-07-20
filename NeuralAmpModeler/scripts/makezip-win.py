import zipfile, os, fileinput, glob, string, sys, shutil

scriptpath = os.path.dirname(os.path.realpath(__file__))
projectpath = os.path.abspath(os.path.join(scriptpath, os.pardir))

IPLUG2_ROOT = "..\..\iPlug2"

sys.path.insert(0, os.path.join(scriptpath, IPLUG2_ROOT + "\Scripts"))

from get_archive_name import get_archive_name


def bundle_entries(bundle_path):
    """(source, arcname) for every file in a VST3 bundle, rooted at the bundle
    directory so Contents\\Resources\\ThirdPartyNotices.txt survives zipping."""
    parent = os.path.dirname(bundle_path)
    entries = []

    for root, _, filenames in os.walk(bundle_path):
        for name in filenames:
            full = os.path.join(root, name)
            entries.append((full, os.path.relpath(full, parent)))

    # os.walk is silent on a missing directory, which would ship a zip with no
    # plug-in in it and still exit 0. Fail instead.
    if not entries:
        raise RuntimeError("no files found in bundle: " + bundle_path)

    return entries


def main():
    if len(sys.argv) != 3:
        print("Usage: make_zip.py demo[0/1] zip[0/1]")
        sys.exit(1)
    else:
        demo = int(sys.argv[1])
        zip = int(sys.argv[2])

    dir = projectpath + "\\build-win\\out"

    if os.path.exists(dir):
        shutil.rmtree(dir)

    os.makedirs(dir)

    files = []

    if not zip:
        installer = "\\build-win\\installer\\AntiStatic Installer.exe"

        if demo:
            installer = "\\build-win\\installer\\AntiStatic Demo Installer.exe"

        files = [
            (f, os.path.basename(f))
            for f in [
                projectpath + installer,
                projectpath + "\\installer\\changelog.txt",
                projectpath + "\\installer\\known-issues.txt",
                projectpath + "\\manual\\NeuralAmpModeler manual.pdf",
            ]
        ]
    else:
        # The VST3 goes in whole, not just its binary: the plug-in resolves the
        # Third Party Notices link out of Contents\Resources at runtime, and
        # flattening the bundle here is what left that link dead on Windows
        # while macOS (which cp -R's the bundle) worked.
        files = bundle_entries(projectpath + "\\build-win\\AntiStatic.vst3")

        # Same file again beside the standalone, which looks next to its exe.
        files += [
            (f, os.path.basename(f))
            for f in [
                projectpath + "\\build-win\\AntiStatic_x64.exe",
                projectpath + "\\build-win\\ThirdPartyNotices.txt",
            ]
        ]

    zipname = get_archive_name(projectpath, "win", "demo" if demo == 1 else "full")

    zf = zipfile.ZipFile(
        projectpath + "\\build-win\\out\\" + zipname + ".zip", mode="w"
    )

    for src, arcname in files:
        print("adding " + src)
        zf.write(src, arcname, zipfile.ZIP_DEFLATED)

    zf.close()
    print("wrote " + zipname)

    zf = zipfile.ZipFile(
        projectpath + "\\build-win\\out\\" + zipname + "-pdbs.zip", mode="w"
    )

    # Both projects set TargetName to BINARY_NAME, so they share one PDB path
    # rather than getting per-target names. Glob so this can't drift again.
    files = [
        (f, os.path.basename(f))
        for f in glob.glob(projectpath + "\\build-win\\pdbs\\*.pdb")
    ]

    for src, arcname in files:
        print("adding " + src)
        zf.write(src, arcname, zipfile.ZIP_DEFLATED)

    zf.close()
    print("wrote " + zipname)


if __name__ == "__main__":
    main()
