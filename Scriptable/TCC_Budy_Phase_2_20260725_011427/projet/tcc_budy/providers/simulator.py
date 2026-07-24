import time

from tcc_budy.providers.base import ResponseProvider
from tcc_budy.support.errors import ProviderError


class SimulatorProvider(ResponseProvider):
    def __init__(self, delay_seconds: float = 0.25):
        self.delay_seconds = max(0.0, float(delay_seconds))

    @property
    def name(self) -> str:
        return "simulator"

    def respond(self, messages) -> str:
        time.sleep(self.delay_seconds)
        text = messages[-1]["content"] if messages else ""
        cleaned = " ".join((text or "").split())
        lowered = cleaned.lower()

        if lowered == "/erreur":
            raise ProviderError("La réponse simulée a volontairement échoué.")
        if not cleaned:
            return "Pouvez-vous préciser ce qui vous préoccupe ?"
        if any(word in lowered for word in ("danger", "suicide", "mourir", "overdose")):
            return (
                "Votre sécurité passe en premier. Êtes-vous en danger immédiat ou avez-vous "
                "l'intention de vous faire du mal maintenant ? Dans ce cas, contactez immédiatement "
                "les secours ou une personne de confiance présente avec vous."
            )
        if any(word in lowered for word in ("peur", "angoisse", "anxieux", "panique")):
            return (
                "Quelle pensée précise accompagne cette inquiétude, et quels faits la "
                "confirment aujourd'hui ?"
            )
        if any(word in lowered for word in ("alcool", "cocaïne", "cocaine", "consommé", "rechute")):
            return (
                "Avant d'analyser la situation, avez-vous un symptôme physique inquiétant "
                "ou un risque immédiat ? Ensuite, nous pourrons distinguer ce qui s'est "
                "passé, les déclencheurs et le prochain pas réaliste."
            )
        return (
            "Je vous suis. Quel résultat vous aiderait le plus maintenant : être écouté, "
            "comprendre, prendre une décision ou définir une petite action ?"
        )
