import time

from tcc_budy.providers.base import ResponseProvider
from tcc_budy.support.errors import ProviderError


class SimulatorProvider(ResponseProvider):
    """Simulateur local contextuel utilisé avant l'activation d'OpenAI."""

    def __init__(self, delay_seconds: float = 0.35):
        self.delay_seconds = max(0.0, float(delay_seconds))

    def respond(self, text: str) -> str:
        time.sleep(self.delay_seconds)
        cleaned = " ".join((text or "").split())
        lowered = cleaned.lower()

        if lowered == "/erreur":
            raise ProviderError("La réponse simulée a volontairement échoué.")
        if not cleaned:
            return "Pouvez-vous préciser ce qui vous préoccupe ?"

        if any(term in lowered for term in (
            "consommé", "consomme", "alcool", "cocaïne", "cocaine",
            "drogue", "défoncé", "defonce"
        )):
            return (
                "Je comprends que vous avez consommé. Avant d’aller plus loin, "
                "avez-vous actuellement un symptôme physique inquiétant, comme "
                "une douleur dans la poitrine, une difficulté à respirer, un "
                "malaise ou une forte confusion ?"
            )

        if "ma femme" in lowered or "mon conjoint" in lowered or "ma conjointe" in lowered:
            return (
                "Son arrivée semble rendre la situation plus urgente. "
                "Qu’est-ce que vous craignez précisément lorsqu’elle arrivera ?"
            )

        if any(term in lowered for term in (
            "pas travaillé", "pas travaille", "n'ai pas travaillé",
            "n’ai pas travaillé", "absent"
        )):
            return (
                "Le fait de ne pas avoir travaillé semble vous inquiéter. "
                "Quelles conséquences sont déjà certaines, et lesquelles sont "
                "pour l’instant des craintes ?"
            )

        if any(term in lowered for term in (
            "perdre mon boulot", "perdre mon travail", "licencié", "licencie",
            "viré", "vire"
        )):
            return (
                "Vous avez peur de perdre votre travail. Avez-vous aujourd’hui "
                "un élément concret indiquant que cette conséquence est décidée, "
                "ou est-ce surtout l’anticipation de ce qui pourrait arriver ?"
            )

        if any(term in lowered for term in (
            "fatigué", "fatigue", "épuisé", "epuise", "crevé", "creve"
        )):
            return (
                "Vous semblez très fatigué. Avez-vous surtout besoin de récupérer "
                "maintenant, ou de résoudre un problème immédiat avant de pouvoir "
                "vous reposer ?"
            )

        if any(term in lowered for term in (
            "peur", "angoisse", "anxieux", "anxiété", "panique"
        )):
            return (
                "Je comprends que l’inquiétude est forte. Quelle est la pensée "
                "précise qui vous traverse, et que redoutez-vous qu’il se passe ?"
            )

        if any(term in lowered for term in (
            "je ne sais pas", "je sais pas", "aucune idée"
        )):
            return (
                "Ce n’est pas grave de ne pas savoir immédiatement. Ce que vous "
                "ressentez ressemble-t-il davantage à de la peur, de la honte, "
                "de la colère ou de la fatigue ?"
            )

        if "?" in cleaned:
            return (
                "Je vais vous aider à examiner cette question. Quels sont les "
                "faits certains dont vous disposez aujourd’hui ?"
            )

        return (
            "Je vous ai compris. Qu’est-ce qui vous semble le plus urgent à "
            "gérer maintenant : votre état physique, l’arrivée de quelqu’un, "
            "ou les conséquences professionnelles ?"
        )
