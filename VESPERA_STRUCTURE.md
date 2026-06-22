# 🌌 Vespera OS Directory Structure

```text
Aether-1.0.0/
  ├── .github
  │   ├── DISCUSSION_TEMPLATE
  │   │   ├── ideas.yml
  │   │   ├── q-a.yml
  │   │   └── show-and-tell.yml
  │   ├── ISSUE_TEMPLATE
  │   │   ├── bug_report.md
  │   │   ├── bug_report.yml
  │   │   ├── config.yml
  │   │   ├── custom.md
  │   │   ├── custom_suggestion.yml
  │   │   ├── documentation_update.yml
  │   │   ├── feature_request.md
  │   │   ├── feature_request.yml
  │   │   └── question.yml
  │   ├── policies
  │   │   ├── policy-rule-1.md
  │   │   ├── policy-rule-10.md
  │   │   ├── policy-rule-11.md
  │   │   ├── policy-rule-12.md
  │   │   ├── policy-rule-13.md
  │   │   ├── policy-rule-14.md
  │   │   ├── policy-rule-15.md
  │   │   ├── policy-rule-16.md
  │   │   ├── policy-rule-17.md
  │   │   ├── policy-rule-18.md
  │   │   ├── policy-rule-19.md
  │   │   ├── policy-rule-2.md
  │   │   ├── policy-rule-20.md
  │   │   ├── policy-rule-21.md
  │   │   ├── policy-rule-22.md
  │   │   ├── policy-rule-23.md
  │   │   ├── policy-rule-24.md
  │   │   ├── policy-rule-25.md
  │   │   ├── policy-rule-3.md
  │   │   ├── policy-rule-4.md
  │   │   ├── policy-rule-5.md
  │   │   ├── policy-rule-6.md
  │   │   ├── policy-rule-7.md
  │   │   ├── policy-rule-8.md
  │   │   └── policy-rule-9.md
  │   ├── PULL_REQUEST_TEMPLATE
  │   │   ├── pr_documentation.md
  │   │   ├── pr_feature.md
  │   │   ├── pr_hotfix.md
  │   │   └── pr_refactoring.md
  │   ├── workflows
  │   │   ├── jobs
  │   │   │   ├── ci-job-1.yml
  │   │   │   ├── ci-job-10.yml
  │   │   │   ├── ci-job-11.yml
  │   │   │   ├── ci-job-12.yml
  │   │   │   ├── ci-job-13.yml
  │   │   │   ├── ci-job-14.yml
  │   │   │   ├── ci-job-15.yml
  │   │   │   ├── ci-job-16.yml
  │   │   │   ├── ci-job-17.yml
  │   │   │   ├── ci-job-18.yml
  │   │   │   ├── ci-job-19.yml
  │   │   │   ├── ci-job-2.yml
  │   │   │   ├── ci-job-20.yml
  │   │   │   ├── ci-job-21.yml
  │   │   │   ├── ci-job-22.yml
  │   │   │   ├── ci-job-23.yml
  │   │   │   ├── ci-job-24.yml
  │   │   │   ├── ci-job-25.yml
  │   │   │   ├── ci-job-3.yml
  │   │   │   ├── ci-job-4.yml
  │   │   │   ├── ci-job-5.yml
  │   │   │   ├── ci-job-6.yml
  │   │   │   ├── ci-job-7.yml
  │   │   │   ├── ci-job-8.yml
  │   │   │   └── ci-job-9.yml
  │   │   ├── ascension-ci.yml
  │   │   ├── build.yml
  │   │   ├── check-links.yml
  │   │   ├── ci.yml
  │   │   ├── client-check.yml
  │   │   ├── codeql-analysis.yml
  │   │   ├── commit-lint.yml
  │   │   ├── dependabot.yml
  │   │   ├── dependency-review.yml
  │   │   ├── deploy.yml
  │   │   ├── docker-publish.yml
  │   │   ├── greetings.yml
  │   │   ├── labeler.yml
  │   │   ├── lint.yml
  │   │   ├── lock.yml
  │   │   ├── pr-size-labeler.yml
  │   │   ├── pr-title-checker.yml
  │   │   ├── prettier.yml
  │   │   ├── release.yml
  │   │   ├── security-scan.yml
  │   │   ├── stale.yml
  │   │   └── test.yml
  │   ├── CODE_OF_CONDUCT.md
  │   ├── CODEOWNERS
  │   ├── CONTRIBUTING.md
  │   ├── dependabot.yml
  │   ├── FUNDING.yml
  │   ├── labeler.yml
  │   ├── pull_request_template.md
  │   ├── SECURITY.md
  │   └── SUPPORT.md
  ├── .vscode
  │   ├── extensions.json
  │   ├── launch.json
  │   ├── settings.json
  │   └── tasks.json
  ├── aegis-cast
  │   ├── src
  │   │   ├── main.jsx
  │   │   ├── SubtitlesWidget.jsx
  │   │   └── TelemetryWidget.jsx
  │   ├── index.html
  │   ├── package-lock.json
  │   ├── package.json
  │   └── vite.config.js
  ├── Extras
  │   ├── Archive
  │   │   ├── API.md
  │   │   ├── ARCHITECTURE.md
  │   │   ├── CHANGELOG.md
  │   │   ├── cognitive_architecture.md
  │   │   ├── DEPLOYMENT.md
  │   │   ├── DEVELOPER_GUIDE.md
  │   │   ├── FAQ.md
  │   │   ├── GOVERNANCE.md
  │   │   ├── memory_schema.md
  │   │   ├── orb_rendering.md
  │   │   ├── registry_keys.md
  │   │   ├── ROADMAP.md
  │   │   ├── STYLE_GUIDE.md
  │   │   ├── SUPPORT_POLICY.md
  │   │   ├── TESTING.md
  │   │   ├── TROUBLESHOOTING.md
  │   │   ├── voice_processing.md
  │   │   └── WORKSPACE_TELEMETRY.md
  │   ├── BespokeAssets
  │   │   ├── architecture.svg
  │   │   ├── banner.svg
  │   │   ├── memory.svg
  │   │   ├── premium_home_dashboard.png
  │   │   ├── premium_settings_panel.png
  │   │   └── telemetry.svg
  │   ├── CoreCapabilities
  │   │   ├── custom_skills.py
  │   │   └── skills_knowledge.json
  │   └── WhiteGloveServices
  │       ├── build-CognitiveCore.bat
  │       ├── build-CognitiveCore.cmd
  │       ├── build-CognitiveCore.ps1
  │       ├── build-VisionInterface.bat
  │       ├── build-VisionInterface.cmd
  │       ├── build-VisionInterface.ps1
  │       ├── clean-caches.bat
  │       ├── clean-caches.cmd
  │       ├── clean-caches.ps1
  │       ├── deploy-github.bat
  │       ├── deploy-github.cmd
  │       ├── deploy-github.ps1
  │       ├── deploy-vercel.bat
  │       ├── deploy-vercel.cmd
  │       ├── deploy-vercel.ps1
  │       ├── install-admin.bat
  │       ├── install-admin.cmd
  │       ├── install-admin.ps1
  │       ├── install-dev.bat
  │       ├── install-dev.cmd
  │       ├── install-dev.ps1
  │       ├── install-silent.bat
  │       ├── install-silent.cmd
  │       ├── install-silent.ps1
  │       ├── reset-env.bat
  │       ├── reset-env.cmd
  │       ├── reset-env.ps1
  │       ├── start-CognitiveCore.bat
  │       ├── start-CognitiveCore.cmd
  │       ├── start-CognitiveCore.ps1
  │       ├── start-VisionInterface.bat
  │       ├── start-VisionInterface.cmd
  │       ├── start-VisionInterface.ps1
  │       ├── test-all.bat
  │       ├── test-all.cmd
  │       ├── test-all.ps1
  │       ├── uninstall.bat
  │       ├── uninstall.cmd
  │       ├── uninstall.ps1
  │       ├── update-force.bat
  │       ├── update-force.cmd
  │       ├── update-force.ps1
  │       ├── verify_install.bat
  │       ├── verify_install.cmd
  │       └── verify_install.ps1
  ├── lumen-desk
  │   ├── e2e
  │   │   └── landing.spec.ts
  │   ├── public
  │   │   ├── file.svg
  │   │   ├── globe.svg
  │   │   ├── logo.png
  │   │   ├── next.svg
  │   │   ├── vercel.svg
  │   │   └── window.svg
  │   ├── src
  │   │   ├── app
  │   │   │   ├── dashboard
  │   │   │   │   └── page.tsx
  │   │   │   ├── docs
  │   │   │   │   └── page.tsx
  │   │   │   ├── globals.css
  │   │   │   ├── icon.png
  │   │   │   ├── layout.tsx
  │   │   │   └── page.tsx
  │   │   └── components
  │   │       ├── LenisProvider.tsx
  │   │       └── Navigation.tsx
  │   ├── .gitignore
  │   ├── AGENTS.md
  │   ├── CLAUDE.md
  │   ├── eslint.config.mjs
  │   ├── next-env.d.ts
  │   ├── next.config.ts
  │   ├── package-lock.json
  │   ├── package.json
  │   ├── postcss.config.mjs
  │   ├── README.md
  │   ├── tsconfig.json
  │   └── tsconfig.tsbuildinfo
  ├── umbracore
  │   ├── api
  │   │   └── handlers
  │   │       └── routes
  │   ├── data
  │   │   ├── memory.json
  │   │   └── settings.json
  │   ├── NeuralCore
  │   │   ├── extensions
  │   │   ├── wake_system
  │   │   │   ├── __init__.py
  │   │   │   ├── base_wake_plugin.py
  │   │   │   ├── hotkey_wake_plugin.py
  │   │   │   └── keyword_wake_plugin.py
  │   │   ├── __init__.py
  │   │   ├── audio_recovery.py
  │   │   ├── db_doctor.py
  │   │   ├── event_bus.py
  │   │   ├── ExecutiveAssistant.py
  │   │   ├── EyeTracker.py
  │   │   ├── GuardianOverride.py
  │   │   ├── image_generator.py
  │   │   ├── keyboard_listener.py
  │   │   ├── llm_engine.py
  │   │   ├── model_config.py
  │   │   ├── NeuralGraph.py
  │   │   ├── ocr_engine.py
  │   │   ├── OmniScreen.py
  │   │   ├── paths.py
  │   │   ├── PostureGuardian.py
  │   │   ├── proactive_helper.py
  │   │   ├── SemanticSearch.py
  │   │   ├── signal_handler.py
  │   │   ├── SilentSealCrypto.py
  │   │   ├── skills_manager.py
  │   │   ├── system_monitor.py
  │   │   ├── TheArchitect.py
  │   │   ├── TheLibrarian.py
  │   │   ├── ThePsychic.py
  │   │   ├── ThermalGuardian.py
  │   │   ├── vespera_core.py
  │   │   ├── vespera_guardian.py
  │   │   ├── vespera_kernel_supervisor.py
  │   │   ├── vespera_knowledge.py
  │   │   ├── vespera_memory.py
  │   │   ├── vespera_presence.py
  │   │   ├── vespera_runtime.py
  │   │   ├── vespera_scheduler.py
  │   │   ├── vespera_society.py
  │   │   ├── vespera_voice.py
  │   │   ├── VocalAnalyzer.py
  │   │   └── WealthManager.py
  │   ├── skills
  │   │   ├── academic_assistant.py
  │   │   ├── custom_skills.py
  │   │   ├── ide_assistant.py
  │   │   ├── media_control.py
  │   │   ├── pc_optimizer.py
  │   │   ├── skills_knowledge.json
  │   │   └── study_helper.py
  │   ├── sounds
  │   │   ├── hack.wav
  │   │   └── typing.wav
  │   ├── tests
  │   │   ├── conftest.py
  │   │   ├── test_additional_modules.py
  │   │   ├── test_api.py
  │   │   ├── test_audio.py
  │   │   ├── test_core.py
  │   │   ├── test_db_doctor.py
  │   │   ├── test_event_bus.py
  │   │   ├── test_file_indexer.py
  │   │   ├── test_models.py
  │   │   ├── test_settings_manager.py
  │   │   ├── test_utils.py
  │   │   ├── test_vespera_app_resolver.py
  │   │   ├── test_vespera_presence.py
  │   │   └── test_wake_system.py
  │   ├── TheDailyHub
  │   │   ├── FileOrganizer.py
  │   │   └── MorningBriefing.py
  │   ├── V12Cylinders
  │   │   ├── __init__.py
  │   │   ├── AcousticMaestro.py
  │   │   ├── AdaptiveLighting.py
  │   │   ├── app_opener.py
  │   │   ├── AppConductor.py
  │   │   ├── AudioDucking.py
  │   │   ├── AutoInjector.py
  │   │   ├── desktop_ops.py
  │   │   ├── file_indexer.py
  │   │   ├── file_ops.py
  │   │   ├── gaming_monitor.py
  │   │   ├── GenerativeUI.py
  │   │   ├── OBS_Director.py
  │   │   ├── OBS_GlassServer.py
  │   │   ├── research_worker.py
  │   │   ├── screen_ocr.py
  │   │   ├── settings_manager.py
  │   │   ├── ShutdownSymphony.py
  │   │   ├── SilentScholar.py
  │   │   ├── SmartHome_IoT.py
  │   │   ├── startup_manager.py
  │   │   ├── SuperClipboard.py
  │   │   ├── TheBouncer.py
  │   │   ├── TheChauffeur.py
  │   │   ├── TheProducer.py
  │   │   ├── TheWhisper.py
  │   │   ├── vespera_app_resolver.py
  │   │   ├── vespera_safety.py
  │   │   ├── vespera_silent_launcher.py
  │   │   ├── web_services.py
  │   │   └── youtube_player.py
  │   ├── .env
  │   ├── main.py
  │   ├── MorningBriefing.spec
  │   ├── pyproject.toml
  │   ├── pytest.ini
  │   ├── requirements-dev.txt
  │   ├── requirements.txt
  │   ├── setup.py
  │   ├── TheChauffeur.spec
  │   ├── ui_server.py
  │   └── VesperaCore.spec
  ├── VSCodeExtension
  │   ├── out
  │   │   ├── extension.js
  │   │   └── extension.js.map
  │   ├── src
  │   │   └── extension.ts
  │   ├── LICENSE
  │   ├── logo.png
  │   ├── package-lock.json
  │   ├── package.json
  │   ├── README.md
  │   └── tsconfig.json
  ├── wraithglass
  │   ├── public
  │   │   ├── favicon.svg
  │   │   ├── icons.svg
  │   │   ├── tray_icon.ico
  │   │   ├── tray_icon.png
  │   │   └── tray_icon_dark.png
  │   ├── release
  │   │   ├── win-unpacked
  │   │   │   ├── locales
  │   │   │   │   ├── af.pak
  │   │   │   │   ├── am.pak
  │   │   │   │   ├── ar.pak
  │   │   │   │   ├── bg.pak
  │   │   │   │   ├── bn.pak
  │   │   │   │   ├── ca.pak
  │   │   │   │   ├── cs.pak
  │   │   │   │   ├── da.pak
  │   │   │   │   ├── de.pak
  │   │   │   │   ├── el.pak
  │   │   │   │   ├── en-GB.pak
  │   │   │   │   ├── en-US.pak
  │   │   │   │   ├── es-419.pak
  │   │   │   │   ├── es.pak
  │   │   │   │   ├── et.pak
  │   │   │   │   ├── fa.pak
  │   │   │   │   ├── fi.pak
  │   │   │   │   ├── fil.pak
  │   │   │   │   ├── fr.pak
  │   │   │   │   ├── gu.pak
  │   │   │   │   ├── he.pak
  │   │   │   │   ├── hi.pak
  │   │   │   │   ├── hr.pak
  │   │   │   │   ├── hu.pak
  │   │   │   │   ├── id.pak
  │   │   │   │   ├── it.pak
  │   │   │   │   ├── ja.pak
  │   │   │   │   ├── kn.pak
  │   │   │   │   ├── ko.pak
  │   │   │   │   ├── lt.pak
  │   │   │   │   ├── lv.pak
  │   │   │   │   ├── ml.pak
  │   │   │   │   ├── mr.pak
  │   │   │   │   ├── ms.pak
  │   │   │   │   ├── nb.pak
  │   │   │   │   ├── nl.pak
  │   │   │   │   ├── pl.pak
  │   │   │   │   ├── pt-BR.pak
  │   │   │   │   ├── pt-PT.pak
  │   │   │   │   ├── ro.pak
  │   │   │   │   ├── ru.pak
  │   │   │   │   ├── sk.pak
  │   │   │   │   ├── sl.pak
  │   │   │   │   ├── sr.pak
  │   │   │   │   ├── sv.pak
  │   │   │   │   ├── sw.pak
  │   │   │   │   ├── ta.pak
  │   │   │   │   ├── te.pak
  │   │   │   │   ├── th.pak
  │   │   │   │   ├── tr.pak
  │   │   │   │   ├── uk.pak
  │   │   │   │   ├── ur.pak
  │   │   │   │   ├── vi.pak
  │   │   │   │   ├── zh-CN.pak
  │   │   │   │   └── zh-TW.pak
  │   │   │   ├── resources
  │   │   │   │   ├── app.asar.unpacked
  │   │   │   │   ├── client
  │   │   │   │   ├── data
  │   │   │   │   │   ├── memory.json
  │   │   │   │   │   └── settings.json
  │   │   │   │   ├── skills
  │   │   │   │   │   ├── custom_skills.py
  │   │   │   │   │   ├── pc_optimizer.py
  │   │   │   │   │   ├── skills_knowledge.json
  │   │   │   │   │   └── study_helper.py
  │   │   │   │   ├── sounds
  │   │   │   │   │   ├── hack.wav
  │   │   │   │   │   └── typing.wav
  │   │   │   │   ├── .env
  │   │   │   │   ├── AdityaCore.exe
  │   │   │   │   ├── app.asar
  │   │   │   │   └── elevate.exe
  │   │   │   ├── ADITYA.exe
  │   │   │   ├── chrome_100_percent.pak
  │   │   │   ├── chrome_200_percent.pak
  │   │   │   ├── d3dcompiler_47.dll
  │   │   │   ├── ffmpeg.dll
  │   │   │   ├── icudtl.dat
  │   │   │   ├── libEGL.dll
  │   │   │   ├── libGLESv2.dll
  │   │   │   ├── LICENSE.electron.txt
  │   │   │   ├── LICENSES.chromium.html
  │   │   │   ├── resources.pak
  │   │   │   ├── snapshot_blob.bin
  │   │   │   ├── v8_context_snapshot.bin
  │   │   │   ├── vk_swiftshader.dll
  │   │   │   ├── vk_swiftshader_icd.json
  │   │   │   └── vulkan-1.dll
  │   │   ├── ADITYA Setup 1.0.0.exe
  │   │   ├── ADITYA Setup 1.0.0.exe.blockmap
  │   │   └── builder-debug.yml
  │   ├── skills
  │   │   ├── custom_skills.py
  │   │   └── skills_knowledge.json
  │   ├── src
  │   │   ├── BespokeViews
  │   │   │   ├── Browser
  │   │   │   │   └── index.jsx
  │   │   │   ├── Home
  │   │   │   │   ├── GamerDashboard.jsx
  │   │   │   │   ├── index.jsx
  │   │   │   │   ├── StreamerDashboard.jsx
  │   │   │   │   ├── StudentDashboard.jsx
  │   │   │   │   └── SystemSkillsWidget.jsx
  │   │   │   ├── Profile
  │   │   │   │   └── index.jsx
  │   │   │   ├── Settings
  │   │   │   │   ├── AppearanceTab.jsx
  │   │   │   │   ├── GeneralTab.jsx
  │   │   │   │   ├── index.jsx
  │   │   │   │   ├── VoiceTab.jsx
  │   │   │   │   └── WraithglassMemoryEngineTab.jsx
  │   │   │   └── SkillTree
  │   │   │       └── index.jsx
  │   │   ├── constants
  │   │   │   └── index.js
  │   │   ├── CoreMotion
  │   │   │   ├── useBackend.js
  │   │   │   ├── useMagneticHover.js
  │   │   │   ├── useNetworkStatus.js
  │   │   │   └── worker.js
  │   │   ├── SpringBoard
  │   │   │   ├── Atoms
  │   │   │   │   └── Tooltip.jsx
  │   │   │   ├── Molecules
  │   │   │   │   ├── BootSequence.jsx
  │   │   │   │   ├── BottomControls.jsx
  │   │   │   │   ├── ErrorBoundary.jsx
  │   │   │   │   └── StatusBar.jsx
  │   │   │   └── Organisms
  │   │   │       ├── AmbientCanvas.jsx
  │   │   │       ├── FloatingOrb.jsx
  │   │   │       ├── Sidebar.jsx
  │   │   │       ├── Startup.jsx
  │   │   │       └── Visualizer.jsx
  │   │   ├── tests
  │   │   │   ├── App.test.jsx
  │   │   │   ├── Chat.test.jsx
  │   │   │   ├── Orb.test.jsx
  │   │   │   ├── Settings.test.jsx
  │   │   │   └── Sidebar.test.jsx
  │   │   ├── utils
  │   │   │   ├── apiHelper.js
  │   │   │   ├── eventBus.js
  │   │   │   ├── index.js
  │   │   │   ├── logger.js
  │   │   │   ├── rateLimiter.js
  │   │   │   ├── reconnectSocket.js
  │   │   │   ├── safeFileWriter.js
  │   │   │   └── stateManager.js
  │   │   ├── api.js
  │   │   ├── App.jsx
  │   │   ├── index.css
  │   │   └── main.jsx
  │   ├── tests
  │   │   └── visual.spec.js
  │   ├── .eslintignore
  │   ├── .stylelintrc.json
  │   ├── afterPack.cjs
  │   ├── create_installer_assets.py
  │   ├── eslint.config.js
  │   ├── index.html
  │   ├── jsconfig.json
  │   ├── loading.html
  │   ├── main.cjs
  │   ├── package-lock.json
  │   ├── package.json
  │   ├── playwright.config.js
  │   ├── preload.cjs
  │   └── vite.config.js
  ├── .commitlintrc.json
  ├── .coveragerc
  ├── .dockerignore
  ├── .editorconfig
  ├── .env
  ├── .env.example
  ├── .gitattributes
  ├── .gitignore
  ├── .npmrc
  ├── .nvmrc
  ├── .pre-commit-config.yaml
  ├── .prettierignore
  ├── .prettierrc
  ├── .python-version
  ├── build_ascended.ps1
  ├── CITATION.cff
  ├── CONTRIBUTING.md
  ├── docker-compose.yml
  ├── Dockerfile
  ├── generate_structure.py
  ├── install.bat
  ├── install.cmd
  ├── install.ps1
  ├── LICENSE
  ├── mypy.ini
  ├── package.json
  ├── pytest.ini
  ├── readme.md
  ├── refactor_atomic.py
  ├── repair.bat
  ├── ruff.toml
  ├── SECURITY.md
  ├── update.bat
  ├── VESPERA_AI_DETAILS.md
  └── VesperaCore.spec
```