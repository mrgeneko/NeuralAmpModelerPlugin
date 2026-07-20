# Anti-Static (Neural Amp Modeler Plug-in fork)

[![Build](https://github.com/mrgeneko/NeuralAmpModelerPlugin/actions/workflows/build-native.yml/badge.svg)](https://github.com/mrgeneko/NeuralAmpModelerPlugin/actions/workflows/build-native.yml)

A VST3/AudioUnit plug-in\* for [Neural Amp Modeler](https://github.com/sdatkinson/neural-amp-modeler), built with [iPlug2](https://iplug2.github.io).

This is a fork of [sdatkinson/NeuralAmpModelerPlugin](https://github.com/sdatkinson/NeuralAmpModelerPlugin), rebranded "Anti-Static" and built against [mrgeneko/NeuralAmpModelerCore](https://github.com/mrgeneko/NeuralAmpModelerCore) (see that repo's own README for the fork's DSP-side additions -- parametric/knob-controllable models, slimmable models, etc.). On top of that, this repo adds:
- A settings-page overlay exposing a loaded parametric model's own knobs/switches directly in the UI -- continuous knobs, or for discrete parameters, a segmented switch -- sized and laid out to fit however many the model actually declares (up to 12).
- A generic host parameter list (e.g. a DAW's "Controls" view) that reflects a loaded model's real per-parameter names instead of placeholders.

- https://www.youtube.com/user/RunawayThumbtack
- https://github.com/sdatkinson/neural-amp-modeler

## Installing

Builds are on the [Releases page](https://github.com/mrgeneko/NeuralAmpModelerPlugin/releases). Each release carries:

| Asset | What it is |
|---|---|
| `Anti-Static-<version>-mac.dmg` | macOS installer -- VST3, Audio Unit, and standalone app |
| `Anti-Static-<version>-win.zip` | Windows VST3 bundle and standalone app |
| `muffinator_v4_optimal.param.nam` | A parametric demo model (see below) |
| `*-dSYMs.zip`, `*-pdbs.zip` | Debug symbols; only useful for diagnosing crashes |

No model is bundled with the plug-in, and it does nothing until one is loaded. To try the parametric knobs this fork adds, download `muffinator_v4_optimal.param.nam` alongside the plug-in and load it with the Model button. Any standard `.nam` file works too -- [ToneHunt](https://tonehunt.org) has a large library, though ordinary models have no parameters to expose.

On Windows, unzip and drop the `AntiStatic.vst3` folder into `C:\Program Files\Common Files\VST3` (or `%LOCALAPPDATA%\Programs\Common\VST3` if you would rather not need admin rights), then rescan plug-ins in your DAW. Copy `AntiStatic_x64.exe` anywhere you like; it runs on its own.

### A note on unsigned Windows builds

The Windows binaries are not code-signed. The VST3 loads in a DAW without complaint, but the standalone `.exe` will raise a SmartScreen warning the first time you run it -- choose **More info**, then **Run anyway**. If Windows behaves oddly after extracting the zip, right-click the downloaded `.zip` and tick **Unblock** in its properties before extracting.

## Building from source

There are build scripts in [NeuralAmpModeler/scripts/](https://github.com/mrgeneko/NeuralAmpModelerPlugin/tree/main/NeuralAmpModeler/scripts).
The [workflows](https://github.com/mrgeneko/NeuralAmpModelerPlugin/tree/main/.github/workflows) show exactly how they are invoked, including the SDK and prebuilt-library downloads that have to happen first.

Clone with `--recurse-submodules`; the build needs iPlug2, eigen, AudioDSPTools, and NeuralAmpModelerCore. On Windows you will also need Visual Studio with the C++ desktop workload, Python, and (for the installer target only) Inno Setup 6.

## Supported Platforms

The Neural Amp Modeler plugin currently supports Windows 10 (64bit) or later, and macOS 10.15 (Catalina) or later.

For Linux support, there is an LV2 plugin available: https://github.com/mikeoliphant/neural-amp-modeler-lv2.

## About

This is a cleaned up version of [the original iPlug2-based NAM plugin](https://github.com/sdatkinson/iPlug2) with some refactoring to adopt better practices recommended by the developers of iPlug2.
(Thanks [Oli](https://github.com/olilarkin) for your generous suggestions!)

\*could also support AAX, CLAP, Linux, iOS soon.

## Rough edges

### Standalone I/O
The I/O for the standalone doesn't inherit the stability of most plugin hosts (DAWs), so it's a bit sparser on features. For complex routing, the plugin (VST3/AU) inside a plugin host is still the most reliable option.

### Graphics backend
If you're having trouble with NAM crashing before the GUI comes up, then you might have an unsupported graphics configuration. Usually, this is when you have a dedicated graphics card (like an nVIDIA GPU) and you're using the integrated (CPU) graphics on a Windows system. To fix this, Go to the control panel, pick NAM (or your DAW), and make sure that it uses your graphics card. (If you know more and can help fix this, please make an Issue and let me know more!)
