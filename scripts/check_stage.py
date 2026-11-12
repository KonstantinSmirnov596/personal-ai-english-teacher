"""Stage acceptance: runs the suites a stage needs, checks required tests and reports.

Usage: python scripts/check_stage.py <N>
A suite name "gpu@compacto" runs the gpu suite with ``--vt-profile compacto``
(tests/profile_opt.py).
Exit code 0 only when every check passed. A ``live`` suite that was skipped because no key is
saved does not fail the stage but is listed separately in the summary.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPORTS = REPO / "docs" / "reports"

MARKERS = {
    "fast": "not gpu and not e2e and not live",
    "gpu": "gpu",
    "e2e": "e2e",
    "live": "live",
}


@dataclass(frozen=True)
class Stage:
    suites: tuple[str, ...]
    required_tests: tuple[str, ...] = ()
    reports: tuple[str, ...] = ()
    files: tuple[str, ...] = ()
    optional_suites: tuple[str, ...] = ()
    clean_install: bool = False
    scripts: tuple[str, ...] = ()  # acceptance scripts (repo-relative), exit code 0 required


# Required tests of the predecessor (its stages 0-4), kept under the new package name. SPEC 13:
# "all suites of the source project pass under the new name".
PREDECESSOR_TESTS: tuple[str, ...] = (
    "tests.test_scaffold::test_package_imports",
    "tests.gpu.test_stage0::test_tts_stt_loop_wer",
    "tests.gpu.test_stage0::test_word_probabilities_present",
    "tests.gpu.test_stage0::test_espeak_symbols_in_phoneme_vocab",
    "tests.test_sentences::test_abbreviations_do_not_split",
    "tests.test_sentences::test_numbers_do_not_split",
    "tests.test_corrector::test_postprocess_rules",
    "tests.test_corrector::test_retry_once_on_empty_then_ok",
    "tests.test_storage::test_data_dir_and_schema_created",
    "tests.test_llm_client::test_stream_and_extra_params",
    "tests.test_llm_client::test_401",
    "tests.test_llm_client::test_status_mapping",
    "tests.test_llm_client::test_timeout",
    "tests.test_connections::test_log_filter_redacts_keys",
    "tests.test_connections::test_create_stores_key_in_keyring_only",
    "tests.test_security::test_health_requires_cookie",
    "tests.test_security::test_foreign_host_rejected_even_with_cookie",
    "tests.test_security::test_foreign_origin_rejected",
    "tests.test_security::test_websocket_guard",
    "tests.test_security::test_html_has_csp_and_no_cors",
    "tests.test_launcher::test_launcher_serves_and_exits_when_window_closes",
    "tests.gpu.test_secret::test_key_marker_stays_in_keyring",
    "tests.gpu.test_turn_ws::test_turn_through_websocket",
    "tests.gpu.test_turn_ws::test_history_prefix_is_stable",
    "tests.gpu.test_turn_ws::test_interrupt_stops_reply_but_not_corrector",
    "tests.e2e.test_conversation::test_conversation_turn",
    "tests.e2e.test_conversation::test_connection_failure_offers_manual_switch",
    "tests.e2e.test_auto::test_pause_below_threshold_keeps_one_turn",
    "tests.e2e.test_auto::test_pause_above_threshold_splits_turn",
    "tests.e2e.test_conversation::test_space_interrupts_reply",
    "tests.test_stage2_logic::test_text_helpers",
    "tests.test_stage2_logic::test_hint_with_cyrillic_is_rejected_after_retry",
    "tests.test_stage2_logic::test_summary_with_mock",
    "tests.test_stage2_logic::test_synthesis_service_rejects_learner_language_before_any_model_work",
    "tests.gpu.test_speech::test_synthesis_rejects_learner_language",
    "tests.test_stage2_logic::test_pattern_focus_after_three_sessions_and_close_after_three_clean",
    "tests.test_stage2_logic::test_cleanup_removes_audio_older_than_retention",
    "tests.test_stage2_logic::test_delete_all_data_keeps_keys_without_flag",
    "tests.test_stage2_logic::test_vocab_spaced_repetition",
    "tests.e2e.test_stage2_ui::test_helpers_summary_and_vocab",
    "tests.e2e.test_stage2_ui::test_settings_sections",
    "tests.test_pron_logic::test_reference_words_and_merged_units",
    "tests.test_pron_logic::test_american_tolerances",
    "tests.test_pron_logic::test_forced_align_on_synthetic_posteriors",
    "tests.test_pron_logic::test_catalog_matching",
    "tests.test_pron_logic::test_levels_and_thresholds",
    "tests.gpu.test_pron::test_false_alarms_on_native_reading",
    "tests.gpu.test_pron::test_catalog_mistakes_are_flagged_and_named",  # was substitutions
    "tests.gpu.test_pron::test_assessment_time_for_a_five_second_phrase",
    "tests.gpu.test_pron::test_feedback_lowers_sensitivity",
    "tests.gpu.test_pron::test_conversation_marks_only_clear_errors",
    "tests.e2e.test_reading::test_reading_marks_sounds_and_accepts_feedback",
    "tests.e2e.test_pron_marks::test_pronunciation_mark_in_conversation",
    "tests.test_operations::test_second_launch_does_not_start_a_second_core",
    "tests.test_operations::test_no_gpu_is_reported_in_plain_words",
    "tests.test_operations::test_missing_models_are_reported",
    "tests.test_operations::test_log_rotation_keeps_a_bounded_number_of_files",
    "tests.gpu.test_network::test_core_talks_only_to_localhost_and_the_llm",
    "tests.gpu.test_startup::test_startup_time",
    "tests.e2e.test_shortcut::test_shortcut_starts_app_once_and_core_exits_with_window",
)

STAGES: dict[int, Stage] = {
    0: Stage(
        suites=("fast", "gpu", "e2e"),
        required_tests=(
            *PREDECESSOR_TESTS,
            "tests.test_scaffold::test_predecessor_package_name_is_gone",
            "tests.gpu.test_stage0::test_cuda_device_meets_minimum",
            "tests.gpu.test_stage0::test_torch_arch_list_covers_minimum",
            "tests.test_hygiene::test_local_only_files_are_not_published",
            "tests.test_hygiene::test_no_user_profile_paths_or_user_name",
            "tests.test_hygiene::test_no_email_addresses",
            "tests.test_hygiene::test_no_api_keys",
            "tests.test_hygiene::test_no_long_base64_tokens",
            "tests.test_hygiene::test_no_recordings_outside_generated_dirs",
            "tests.test_hygiene::test_cyrillic_only_in_allowed_paths",
            "tests.test_licenses::test_every_locked_package_has_a_license_row",
            "tests.test_licenses::test_no_weights_or_gpl_binaries_tracked",
            "tests.test_licenses::test_non_python_components_reviewed",
            "tests.test_providers::test_templates_match_the_report",
            "tests.test_providers::test_template_endpoints_are_valid",
            "tests.test_connections::test_local_connection_needs_no_key",
            "tests.test_llm_client::test_complete_json_schema",
            "tests.test_llm_client::test_local_server_without_key",
            "tests.test_launcher::test_exit_watchdog_ends_a_process_with_a_stuck_thread",
        ),
        reports=("stage0.md", "licenses.md", "providers.md"),
        files=("uv.lock", "LICENSE"),
    ),
    1: Stage(
        suites=("fast", "gpu", "e2e"),
        optional_suites=("live",),
        required_tests=(
            # 1.1 registry
            "tests.test_l1::test_two_languages_are_discovered",
            "tests.test_l1::test_windows_locale_suggests_a_language",
            "tests.test_l1::test_a_third_language_is_added_by_files_only",
            "tests.test_l1::test_every_language_has_its_files",
            "tests.test_l1::test_core_messages_complete",
            # 1.2 window strings: completeness 100 % for both languages
            "tests.test_i18n::test_every_learner_language_has_a_string_file",
            "tests.test_i18n::test_key_sets_are_identical",
            "tests.test_i18n::test_values_have_the_same_shape",
            "tests.test_i18n::test_no_empty_strings",
            "tests.test_i18n::test_completeness_is_100_percent",
            "tests.test_i18n::test_strings_are_in_their_language",
            "tests.test_i18n::test_spanish_variety_is_latin_american",
            "tests.test_i18n::test_portuguese_variety_is_brazilian",
            # 1.3 prompts
            "tests.test_prompts::test_corrector_prompt_names_the_language_and_marks_keys",
            "tests.test_prompts::test_corrector_example_per_language",
            "tests.test_prompts::test_helper_and_summary_prompts_take_the_language",
            "tests.test_prompts::test_tutor_prompt_is_language_neutral_and_stable",
            # 1.4 note_l1 and migration
            "tests.test_storage::test_migration_note_l1",
            "tests.test_storage::test_session_records_its_language",
            "tests.test_storage::test_builtin_titles_follow_the_language",
            # 1.5 language guard
            "tests.test_lang_guard::test_english_with_names_and_places_passes",
            "tests.test_lang_guard::test_spanish_is_caught",
            "tests.test_lang_guard::test_portuguese_is_caught",
            "tests.test_lang_guard::test_counts_cover_the_plan",
            "tests.test_stage2_logic::test_synthesis_service_rejects_learner_language_before_any_model_work",
            "tests.gpu.test_speech::test_synthesis_rejects_learner_language",
            # 1.6 scenarios
            "tests.test_scenarios::test_ids_exactly_as_in_spec",
            "tests.test_scenarios::test_titles_and_descriptions_in_every_learner_language",
            "tests.test_scenarios::test_english_fields_are_english",
            "tests.test_scenarios::test_no_erp_or_document_workflow",
            "tests.test_scenarios::test_interviews_follow_the_backend_structure",
            # 1.7 mistake keys
            "tests.test_patterns::test_key_set_equals_spec",
            "tests.test_patterns::test_language_marks_match_spec",
            "tests.test_patterns::test_every_key_marked_for_a_language_has_a_name_and_hint_in_it",
            # 1.8 corrector sets
            "tests.test_corrector_sets::test_set_composition",
            "tests.test_corrector_sets::test_cases_are_well_formed",
            # 1.9 window: a conversation in each language, English stays English
            "tests.e2e.test_conversation::test_conversation_turn",
            "tests.e2e.test_languages::test_language_switch_and_portuguese_conversation",
            "tests.e2e.test_stage2_ui::test_helpers_summary_and_vocab",
            # 1.10 Russian locale gone
            "tests.test_hygiene::test_cyrillic_only_in_allowed_paths",
            "tests.test_hygiene::test_cyrillic_allowlist_is_not_stale",
        ),
        reports=("stage1.md",),
        files=("web/i18n/es-419.js", "web/i18n/pt-BR.js"),
    ),
    2: Stage(
        suites=("fast", "gpu", "e2e"),
        optional_suites=("live",),
        required_tests=(
            # 2.1 catalogs
            "tests.test_catalogs::test_entry_sets_as_in_spec",
            "tests.test_catalogs::test_schema",
            "tests.test_catalogs::test_symbols_are_scoring_classes",
            "tests.test_catalogs::test_tips_are_in_their_language",
            "tests.test_catalogs::test_spanish_tips_are_latin_american",
            "tests.test_catalogs::test_portuguese_tips_are_brazilian",
            "tests.test_pron_logic::test_catalog_matching",
            # 2.2 insertions
            "tests.test_catalogs::test_insertions_only_where_the_catalog_says",
            "tests.gpu.test_pron::test_accented_phrase_marks_the_right_words",
            # 2.3 reading phrases
            "tests.test_catalogs::test_reading_coverage",
            "tests.test_catalogs::test_phrase_targets_exist",
            # 2.5 metrics per learner language (SPEC 12)
            "tests.gpu.test_pron::test_false_alarms_on_native_reading[es-419]",
            "tests.gpu.test_pron::test_false_alarms_on_native_reading[pt-BR]",
            "tests.gpu.test_pron::test_catalog_mistakes_are_flagged_and_named[es-419]",
            "tests.gpu.test_pron::test_catalog_mistakes_are_flagged_and_named[pt-BR]",
            "tests.gpu.test_pron::test_assessment_time_for_a_five_second_phrase",
            "tests.gpu.test_pron::test_feedback_lowers_sensitivity",
            "tests.gpu.test_pron::test_conversation_marks_only_clear_errors",
            # 2.6 window, per language
            "tests.e2e.test_reading::test_reading_marks_sounds_and_accepts_feedback",
            "tests.e2e.test_reading::test_reading_in_portuguese",
            "tests.e2e.test_pron_marks::test_pronunciation_mark_in_conversation",
            # the Russian catalog is gone: no Cyrillic anywhere
            "tests.test_hygiene::test_cyrillic_only_in_allowed_paths",
        ),
        reports=("stage2.md",),
        files=(
            "voicetutor/data/l1/es-419/catalog.json",
            "voicetutor/data/l1/pt-BR/catalog.json",
            "docs/reports/data/pron_stage2_es-419.json",
            "docs/reports/data/pron_stage2_pt-BR.json",
        ),
    ),
    3: Stage(
        # SPEC 7: both profiles pass the gpu and e2e suites.
        suites=("fast", "gpu", "e2e", "gpu@compacto", "e2e@compacto"),
        optional_suites=("live",),
        required_tests=(
            # 3.1 hardware detector
            "tests.test_hardware::test_system_detector_reads_this_computer",
            # 3.2 profiles
            "tests.test_profiles::test_profiles_from_measured_free_memory",
            "tests.test_profiles::test_profile_estimate_before_the_wizard",
            "tests.test_profiles::test_unsupported_reasons",
            "tests.test_profiles::test_minimum_hardware_is_supported",
            "tests.test_profiles::test_benchmark_can_lower_the_profile",
            "tests.test_profiles::test_compacto_profile_settings",
            "tests.test_profiles::test_phoneme_model_unloads_after_idle_in_compacto",
            # 3.3 video memory shortage
            "tests.test_hardware::test_out_of_memory_frees_the_phoneme_model_and_retries",
            "tests.test_hardware::test_persistent_out_of_memory_gives_a_clear_error",
            "tests.gpu.test_vram::test_core_survives_video_memory_pressure",
            # 3.4 installer requirements check
            "tests.test_requirements_ps1::test_good_machine_passes",
            "tests.test_requirements_ps1::test_blocking_failures",
            "tests.test_requirements_ps1::test_messages_are_complete_in_three_languages",
            "tests.test_requirements_ps1::test_invoke_reports_and_links_the_docs",
            "tests.test_requirements_ps1::test_setup_checks_before_any_download",
            # 3.5 first-run wizard, both languages
            "tests.e2e.test_wizard::test_first_run_wizard[es-419]",
            "tests.e2e.test_wizard::test_first_run_wizard[pt-BR]",
            # 3.6 unsupported hardware: core by injection, window
            "tests.test_unsupported::test_unsupported_hardware_is_explained_and_models_stay_unloaded",
            "tests.e2e.test_unsupported_window::test_unsupported_screen_explains_why",
            # 3.7 run-time notices
            "tests.test_hardware::test_notices_for_battery_and_changed_hardware",
            "tests.test_hardware::test_notices_are_dismissed_once_per_run",
            "tests.test_hardware::test_hello_carries_profile_and_notices",
            # wizard step 3: no download at run time (CLAUDE.md hard constraint)
            "tests.test_hardware::test_models_status_and_load_without_download",
            # docs/<lang>/hardware.md: the wizard and the installer link to its anchors
            "tests.test_user_docs::test_same_structure_in_every_language",
            "tests.test_user_docs::test_every_check_has_an_anchor",
            "tests.test_user_docs::test_installer_check_ids_have_anchors",
        ),
        reports=("stage3.md",),
        files=(
            "scripts/requirements.ps1",
            "scripts/requirements.messages.json",
            "web/js/wizard.js",
            "docs/en/hardware.md",
            "docs/es/hardware.md",
            "docs/pt-BR/hardware.md",
        ),
        # 3.8 profile acceptance: compacto peak <= 5.0 GB, WER delta <= 2 pp
        scripts=("scripts/bench_profiles.py",),
    ),
}


@dataclass
class SuiteResult:
    name: str
    exit_code: int
    passed: set[str] = field(default_factory=set)
    failed: set[str] = field(default_factory=set)
    skipped: dict[str, str] = field(default_factory=dict)


def run_suite(name: str, out_dir: Path) -> SuiteResult:
    marker, _, profile = name.partition("@")
    xml_path = out_dir / f"{name.replace('@', '-')}.xml"
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        MARKERS[marker],
        f"--junitxml={xml_path}",
        "-o",
        "junit_family=xunit2",
    ]
    if profile:
        cmd += ["--vt-profile", profile]
    print(f"=== suite: {name} ===", flush=True)
    proc = subprocess.run(cmd, cwd=REPO, env=os.environ.copy(), check=False)
    result = SuiteResult(name=name, exit_code=proc.returncode)
    if not xml_path.exists():
        return result
    root = ET.parse(xml_path).getroot()
    for case in root.iter("testcase"):
        test_id = f"{case.get('classname', '')}::{case.get('name', '')}"
        if case.find("failure") is not None or case.find("error") is not None:
            result.failed.add(test_id)
        elif (skip := case.find("skipped")) is not None:
            result.skipped[test_id] = skip.get("message", "")
        else:
            result.passed.add(test_id)
    return result


def _matches(required: str, test_id: str) -> bool:
    # Parametrized tests carry a "[...]" suffix; any parametrization counts.
    return test_id == required or test_id.startswith(required + "[")


# TBD/TODO/??? anywhere, or a line that is nothing but an upper-case token (a template slot).
_PLACEHOLDER = re.compile(r"\b(TBD|TODO)\b|\?\?\?|^[A-Z][A-Z_]{3,}$")


def check_report(path: Path) -> list[str]:
    problems: list[str] = []
    if not path.exists():
        return [f"report missing: {path.relative_to(REPO)}"]
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return [f"report empty: {path.relative_to(REPO)}"]
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if _PLACEHOLDER.search(stripped):
            problems.append(f"{path.name}:{lineno}: placeholder left: {stripped[:80]}")
        if not stripped.startswith("|") or re.fullmatch(r"\|[\s:|-]+\|", stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if any(c == "" for c in cells):
            problems.append(f"{path.name}:{lineno}: table row has an empty cell")
    return problems


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("usage: check_stage.py <N>")
        return 2
    target = int(sys.argv[1])
    if target not in STAGES:
        print(f"stage {target} has no acceptance definition yet")
        return 2

    stages = [STAGES[n] for n in sorted(STAGES) if n <= target]
    suites: list[str] = []
    optional: set[str] = set()
    for st in stages:
        for s in st.suites:
            if s not in suites:
                suites.append(s)
        optional.update(st.optional_suites)
    for s in optional:
        if s not in suites:
            suites.append(s)

    problems: list[str] = []
    notes: list[str] = []
    results: dict[str, SuiteResult] = {}
    with tempfile.TemporaryDirectory(prefix="check_stage_") as tmp:
        for s in suites:
            res = run_suite(s, Path(tmp))
            results[s] = res
            if res.exit_code not in (0, 5):
                problems.append(f"suite {s}: pytest exit code {res.exit_code}")

    for s in optional:
        res = results[s]
        if not res.passed and not res.failed and res.skipped:
            reasons = sorted(set(res.skipped.values()))
            notes.append(f"suite {s} skipped: {'; '.join(reasons)[:200]}")

    all_passed = set().union(*(r.passed for r in results.values()))
    all_seen = all_passed | set().union(*(r.failed | set(r.skipped) for r in results.values()))
    for st in stages:
        for req in st.required_tests:
            if any(_matches(req, t) for t in all_passed):
                continue
            if any(_matches(req, t) for t in all_seen):
                problems.append(f"required test did not pass: {req}")
            else:
                problems.append(f"required test not found: {req}")
        for rep in st.reports:
            problems.extend(check_report(REPORTS / rep))
        for f in st.files:
            if not (REPO / f).exists():
                problems.append(f"required file missing: {f}")

    for st in stages:
        for script in st.scripts:
            print(f"=== acceptance script: {script} ===", flush=True)
            proc = subprocess.run(
                [sys.executable, str(REPO / script)], cwd=REPO, env=os.environ.copy(), check=False
            )
            if proc.returncode != 0:
                problems.append(f"acceptance script failed: {script} (exit {proc.returncode})")

    clean_note = ""
    if any(st.clean_install for st in stages):
        print("=== setup from scratch on a clean copy ===", flush=True)
        clean = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "check_clean_install.py")],
            cwd=REPO,
            env=os.environ.copy(),
            check=False,
        )
        clean_note = "passed" if clean.returncode == 0 else "FAILED"
        if clean.returncode != 0:
            problems.append("setup from scratch failed (scripts/check_clean_install.py)")

    print()
    print(f"=== stage {target} summary ===")
    for s in suites:
        r = results[s]
        print(
            f"  {s:12}: exit {r.exit_code}, passed {len(r.passed)}, "
            f"failed {len(r.failed)}, skipped {len(r.skipped)}"
        )
    if clean_note:
        print(f"  clean install: {clean_note}")
    for n in notes:
        print(f"  NOTE: {n}")
    for p in problems:
        print(f"  FAIL: {p}")
    if problems:
        print(f"stage {target}: NOT accepted")
        return 1
    print(f"stage {target}: accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
