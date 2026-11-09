"""Hydroqc custom types."""

# pylint: disable=invalid-name
from typing import TypedDict


class DTDataResultsTyping(TypedDict, total=False):
    """DT winter period data (legacy format).

    Note: montantEconPerteVSTarifBase may not be available when comparison
    data from previous billing is unavailable.
    """

    dateDebut: str
    dateFin: str
    dateDernMaj: str
    hrsCritiquesAppelee: str
    hrsCritiquesAppeleesMax: str
    montantEconPerteVSTarifBase: float
    nbJoursTotauxHiver: int
    nbJoursDernMaj: int
    etatHiver: str


class DTDataTyping(TypedDict, total=True):
    """FlexD data json output format."""

    success: bool
    results: list[DTDataResultsTyping]
