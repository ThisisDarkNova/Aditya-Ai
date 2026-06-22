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
│   ├── PULL_REQUEST_TEMPLATE
│   │   ├── pr_documentation.md
│   │   ├── pr_feature.md
│   │   ├── pr_hotfix.md
│   │   └── pr_refactoring.md
│   ├── workflows
│   │   ├── jobs
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
├── apps
│   ├── lumen-desk
│   │   ├── e2e
│   │   │   └── landing.spec.ts
│   │   ├── public
│   │   │   ├── file.svg
│   │   │   ├── globe.svg
│   │   │   ├── logo.png
│   │   │   ├── next.svg
│   │   │   ├── vercel.svg
│   │   │   └── window.svg
│   │   ├── src
│   │   │   ├── app
│   │   │   │   ├── dashboard
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── docs
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── globals.css
│   │   │   │   ├── icon.png
│   │   │   │   ├── layout.tsx
│   │   │   │   └── page.tsx
│   │   │   └── components
│   │   │       ├── LenisProvider.tsx
│   │   │       └── Navigation.tsx
│   │   ├── .gitignore
│   │   ├── AGENTS.md
│   │   ├── CLAUDE.md
│   │   ├── eslint.config.mjs
│   │   ├── next-env.d.ts
│   │   ├── next.config.ts
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   ├── postcss.config.mjs
│   │   ├── README.md
│   │   ├── tsconfig.json
│   │   └── tsconfig.tsbuildinfo
│   ├── marginalia
│   │   ├── src
│   │   │   └── extension.ts
│   │   ├── LICENSE
│   │   ├── logo.png
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   ├── README.md
│   │   └── tsconfig.json
│   └── wraithglass
│       ├── public
│       │   ├── favicon.svg
│       │   ├── icons.svg
│       │   ├── tray_icon.ico
│       │   ├── tray_icon.png
│       │   └── tray_icon_dark.png
│       ├── release
│       │   ├── win-unpacked
│       │   │   ├── locales
│       │   │   │   ├── af.pak
│       │   │   │   ├── am.pak
│       │   │   │   ├── ar.pak
│       │   │   │   ├── bg.pak
│       │   │   │   ├── bn.pak
│       │   │   │   ├── ca.pak
│       │   │   │   ├── cs.pak
│       │   │   │   ├── da.pak
│       │   │   │   ├── de.pak
│       │   │   │   ├── el.pak
│       │   │   │   ├── en-GB.pak
│       │   │   │   ├── en-US.pak
│       │   │   │   ├── es-419.pak
│       │   │   │   ├── es.pak
│       │   │   │   ├── et.pak
│       │   │   │   ├── fa.pak
│       │   │   │   ├── fi.pak
│       │   │   │   ├── fil.pak
│       │   │   │   ├── fr.pak
│       │   │   │   ├── gu.pak
│       │   │   │   ├── he.pak
│       │   │   │   ├── hi.pak
│       │   │   │   ├── hr.pak
│       │   │   │   ├── hu.pak
│       │   │   │   ├── id.pak
│       │   │   │   ├── it.pak
│       │   │   │   ├── ja.pak
│       │   │   │   ├── kn.pak
│       │   │   │   ├── ko.pak
│       │   │   │   ├── lt.pak
│       │   │   │   ├── lv.pak
│       │   │   │   ├── ml.pak
│       │   │   │   ├── mr.pak
│       │   │   │   ├── ms.pak
│       │   │   │   ├── nb.pak
│       │   │   │   ├── nl.pak
│       │   │   │   ├── pl.pak
│       │   │   │   ├── pt-BR.pak
│       │   │   │   ├── pt-PT.pak
│       │   │   │   ├── ro.pak
│       │   │   │   ├── ru.pak
│       │   │   │   ├── sk.pak
│       │   │   │   ├── sl.pak
│       │   │   │   ├── sr.pak
│       │   │   │   ├── sv.pak
│       │   │   │   ├── sw.pak
│       │   │   │   ├── ta.pak
│       │   │   │   ├── te.pak
│       │   │   │   ├── th.pak
│       │   │   │   ├── tr.pak
│       │   │   │   ├── uk.pak
│       │   │   │   ├── ur.pak
│       │   │   │   ├── vi.pak
│       │   │   │   ├── zh-CN.pak
│       │   │   │   └── zh-TW.pak
│       │   │   ├── resources
│       │   │   │   ├── app.asar.unpacked
│       │   │   │   ├── client
│       │   │   │   ├── data
│       │   │   │   │   ├── memory.json
│       │   │   │   │   └── settings.json
│       │   │   │   ├── skills
│       │   │   │   │   ├── custom_skills.py
│       │   │   │   │   ├── pc_optimizer.py
│       │   │   │   │   ├── skills_knowledge.json
│       │   │   │   │   └── study_helper.py
│       │   │   │   ├── sounds
│       │   │   │   │   ├── hack.wav
│       │   │   │   │   └── typing.wav
│       │   │   │   ├── .env
│       │   │   │   ├── AdityaCore.exe
│       │   │   │   ├── app.asar
│       │   │   │   └── elevate.exe
│       │   │   ├── ADITYA.exe
│       │   │   ├── chrome_100_percent.pak
│       │   │   ├── chrome_200_percent.pak
│       │   │   ├── d3dcompiler_47.dll
│       │   │   ├── ffmpeg.dll
│       │   │   ├── icudtl.dat
│       │   │   ├── libEGL.dll
│       │   │   ├── libGLESv2.dll
│       │   │   ├── LICENSE.electron.txt
│       │   │   ├── LICENSES.chromium.html
│       │   │   ├── resources.pak
│       │   │   ├── snapshot_blob.bin
│       │   │   ├── v8_context_snapshot.bin
│       │   │   ├── vk_swiftshader.dll
│       │   │   ├── vk_swiftshader_icd.json
│       │   │   └── vulkan-1.dll
│       │   ├── ADITYA Setup 1.0.0.exe
│       │   ├── ADITYA Setup 1.0.0.exe.blockmap
│       │   └── builder-debug.yml
│       ├── skills
│       │   ├── custom_skills.py
│       │   └── skills_knowledge.json
│       ├── src
│       │   ├── BespokeViews
│       │   │   ├── Browser
│       │   │   │   └── index.jsx
│       │   │   ├── Home
│       │   │   │   ├── GamerDashboard.jsx
│       │   │   │   ├── index.jsx
│       │   │   │   ├── StreamerDashboard.jsx
│       │   │   │   ├── StudentDashboard.jsx
│       │   │   │   └── SystemSkillsWidget.jsx
│       │   │   ├── Profile
│       │   │   │   └── index.jsx
│       │   │   ├── Settings
│       │   │   │   ├── AppearanceTab.jsx
│       │   │   │   ├── GeneralTab.jsx
│       │   │   │   ├── index.jsx
│       │   │   │   ├── VoiceTab.jsx
│       │   │   │   └── WraithglassMemoryEngineTab.jsx
│       │   │   └── SkillTree
│       │   │       └── index.jsx
│       │   ├── constants
│       │   │   └── index.js
│       │   ├── CoreMotion
│       │   │   ├── useBackend.js
│       │   │   ├── useMagneticHover.js
│       │   │   ├── useNetworkStatus.js
│       │   │   └── worker.js
│       │   ├── SpringBoard
│       │   │   ├── Atoms
│       │   │   │   └── Tooltip.jsx
│       │   │   ├── Molecules
│       │   │   │   ├── BootSequence.jsx
│       │   │   │   ├── BottomControls.jsx
│       │   │   │   ├── ErrorBoundary.jsx
│       │   │   │   └── StatusBar.jsx
│       │   │   └── Organisms
│       │   │       ├── AmbientCanvas.jsx
│       │   │       ├── FloatingOrb.jsx
│       │   │       ├── Sidebar.jsx
│       │   │       ├── Startup.jsx
│       │   │       └── Visualizer.jsx
│       │   ├── tests
│       │   │   ├── App.test.jsx
│       │   │   ├── Chat.test.jsx
│       │   │   ├── Orb.test.jsx
│       │   │   ├── Settings.test.jsx
│       │   │   └── Sidebar.test.jsx
│       │   ├── utils
│       │   │   ├── apiHelper.js
│       │   │   ├── eventBus.js
│       │   │   ├── index.js
│       │   │   ├── logger.js
│       │   │   ├── rateLimiter.js
│       │   │   ├── reconnectSocket.js
│       │   │   ├── safeFileWriter.js
│       │   │   └── stateManager.js
│       │   ├── api.js
│       │   ├── App.jsx
│       │   ├── index.css
│       │   └── main.jsx
│       ├── tests
│       │   └── visual.spec.js
│       ├── .eslintignore
│       ├── .stylelintrc.json
│       ├── afterPack.cjs
│       ├── create_installer_assets.py
│       ├── eslint.config.js
│       ├── index.html
│       ├── jsconfig.json
│       ├── loading.html
│       ├── main.cjs
│       ├── package-lock.json
│       ├── package.json
│       ├── playwright.config.js
│       ├── preload.cjs
│       └── vite.config.js
├── assets
│   ├── architecture.svg
│   ├── banner.svg
│   ├── memory.svg
│   ├── premium_home_dashboard.png
│   ├── premium_settings_panel.png
│   └── telemetry.svg
├── docs
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── cognitive_architecture.md
│   ├── DEPLOYMENT.md
│   ├── DEVELOPER_GUIDE.md
│   ├── FAQ.md
│   ├── GOVERNANCE.md
│   ├── memory_schema.md
│   ├── orb_rendering.md
│   ├── registry_keys.md
│   ├── ROADMAP.md
│   ├── STYLE_GUIDE.md
│   ├── SUPPORT_POLICY.md
│   ├── TESTING.md
│   ├── TROUBLESHOOTING.md
│   ├── voice_processing.md
│   └── WORKSPACE_TELEMETRY.md
├── packages
│   ├── aegis-cast
│   │   ├── src
│   │   │   ├── main.jsx
│   │   │   ├── SubtitlesWidget.jsx
│   │   │   └── TelemetryWidget.jsx
│   │   ├── index.html
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   └── vite.config.js
│   └── umbracore
│       ├── api
│       │   ├── handlers
│       │   │   └── routes
│       │   ├── __init__.py
│       │   └── ui_server.py
│       ├── automation
│       │   ├── __init__.py
│       │   ├── file_organizer.py
│       │   ├── morning_briefing.py
│       │   ├── obs_director.py
│       │   ├── obs_glass_server.py
│       │   ├── shutdown_symphony.py
│       │   ├── the_chauffeur.py
│       │   └── the_producer.py
│       ├── core
│       │   ├── wake_system
│       │   │   ├── __init__.py
│       │   │   ├── base_wake_plugin.py
│       │   │   ├── hotkey_wake_plugin.py
│       │   │   └── keyword_wake_plugin.py
│       │   ├── __init__.py
│       │   ├── acoustic_maestro.py
│       │   ├── adaptive_lighting.py
│       │   ├── app_conductor.py
│       │   ├── app_opener.py
│       │   ├── architect.py
│       │   ├── audio_ducking.py
│       │   ├── audio_recovery.py
│       │   ├── auto_injector.py
│       │   ├── bouncer.py
│       │   ├── db_doctor.py
│       │   ├── desktop_ops.py
│       │   ├── event_bus.py
│       │   ├── executive_assistant.py
│       │   ├── eye_tracker.py
│       │   ├── file_indexer.py
│       │   ├── file_ops.py
│       │   ├── gaming_monitor.py
│       │   ├── generative_ui.py
│       │   ├── guardian_override.py
│       │   ├── image_generator.py
│       │   ├── keyboard_listener.py
│       │   ├── librarian.py
│       │   ├── llm_engine.py
│       │   ├── model_config.py
│       │   ├── neural_graph.py
│       │   ├── ocr_engine.py
│       │   ├── omni_screen.py
│       │   ├── paths.py
│       │   ├── posture_guardian.py
│       │   ├── proactive_helper.py
│       │   ├── psychic.py
│       │   ├── research_worker.py
│       │   ├── screen_ocr.py
│       │   ├── semantic_search.py
│       │   ├── settings_manager.py
│       │   ├── signal_handler.py
│       │   ├── silent_scholar.py
│       │   ├── silent_seal_crypto.py
│       │   ├── skills_manager.py
│       │   ├── smart_home_iot.py
│       │   ├── startup_manager.py
│       │   ├── super_clipboard.py
│       │   ├── thermal_guardian.py
│       │   ├── vespera_app_resolver.py
│       │   ├── vespera_core.py
│       │   ├── vespera_guardian.py
│       │   ├── vespera_kernel_supervisor.py
│       │   ├── vespera_knowledge.py
│       │   ├── vespera_memory.py
│       │   ├── vespera_presence.py
│       │   ├── vespera_runtime.py
│       │   ├── vespera_safety.py
│       │   ├── vespera_scheduler.py
│       │   ├── vespera_silent_launcher.py
│       │   ├── vespera_society.py
│       │   ├── vespera_voice.py
│       │   ├── vocal_analyzer.py
│       │   ├── wealth_manager.py
│       │   ├── web_services.py
│       │   ├── whisper.py
│       │   └── youtube_player.py
│       ├── data
│       │   ├── memory.json
│       │   └── settings.json
│       ├── skills
│       │   ├── academic_assistant.py
│       │   ├── custom_skills.py
│       │   ├── ide_assistant.py
│       │   ├── media_control.py
│       │   ├── pc_optimizer.py
│       │   ├── skills_knowledge.json
│       │   └── study_helper.py
│       ├── sounds
│       │   ├── hack.wav
│       │   └── typing.wav
│       ├── telemetry
│       │   ├── __init__.py
│       │   └── system_monitor.py
│       ├── tests
│       │   ├── conftest.py
│       │   ├── test_additional_modules.py
│       │   ├── test_api.py
│       │   ├── test_audio.py
│       │   ├── test_core.py
│       │   ├── test_db_doctor.py
│       │   ├── test_event_bus.py
│       │   ├── test_file_indexer.py
│       │   ├── test_models.py
│       │   ├── test_settings_manager.py
│       │   ├── test_utils.py
│       │   ├── test_vespera_app_resolver.py
│       │   ├── test_vespera_presence.py
│       │   └── test_wake_system.py
│       ├── .env
│       ├── main.py
│       ├── pyproject.toml
│       ├── pytest.ini
│       ├── requirements-dev.txt
│       ├── requirements.txt
│       ├── setup.py
│       └── VesperaCore.spec
├── scripts
│   ├── build-umbracore.bat
│   ├── build-umbracore.cmd
│   ├── build-umbracore.ps1
│   ├── build-wraithglass.bat
│   ├── build-wraithglass.cmd
│   ├── build-wraithglass.ps1
│   ├── clean-caches.bat
│   ├── clean-caches.cmd
│   ├── clean-caches.ps1
│   ├── deploy-github.bat
│   ├── deploy-github.cmd
│   ├── deploy-github.ps1
│   ├── deploy-vercel.bat
│   ├── deploy-vercel.cmd
│   ├── deploy-vercel.ps1
│   ├── install-admin.bat
│   ├── install-admin.cmd
│   ├── install-admin.ps1
│   ├── install-dev.bat
│   ├── install-dev.cmd
│   ├── install-dev.ps1
│   ├── install-silent.bat
│   ├── install-silent.cmd
│   ├── install-silent.ps1
│   ├── reset-env.bat
│   ├── reset-env.cmd
│   ├── reset-env.ps1
│   ├── start-umbracore.bat
│   ├── start-umbracore.cmd
│   ├── start-umbracore.ps1
│   ├── start-wraithglass.bat
│   ├── start-wraithglass.cmd
│   ├── start-wraithglass.ps1
│   ├── test-all.bat
│   ├── test-all.cmd
│   ├── test-all.ps1
│   ├── uninstall.bat
│   ├── uninstall.cmd
│   ├── uninstall.ps1
│   ├── update-force.bat
│   ├── update-force.cmd
│   ├── update-force.ps1
│   ├── verify_install.bat
│   ├── verify_install.cmd
│   └── verify_install.ps1
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
└── VESPERA_STRUCTURE.md
```