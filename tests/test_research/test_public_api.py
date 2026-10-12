"""The package's Python contract is exactly the thirteen names it exports."""

import agentic_mbse.research as research

PUBLIC_NAMES = {
    "register",
    "SourceMetadata",
    "UrlSource",
    "LocalPdfSource",
    "KeyedFileSource",
    "RegistrationResult",
    "RegistrationError",
    "RegistryPaths",
    "default_paths",
    "load_manifest_rows",
    "HoldoutGuard",
    "HoldoutMatch",
    "load_holdout_guard",
}


def test_all_is_the_thirteen_public_names():
    assert len(research.__all__) == len(set(research.__all__))
    assert set(research.__all__) == PUBLIC_NAMES


def test_every_public_name_is_importable_from_the_package():
    for name in research.__all__:
        assert getattr(research, name) is not None
