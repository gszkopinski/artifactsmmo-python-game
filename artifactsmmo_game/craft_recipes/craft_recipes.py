"""Craft Recipes."""

from artifactsmmo_sdk import ArtifactsClient


class CraftRecipes:
    """Craft Recipes."""

    def __init__(
        self,
        perso: ArtifactsClient,
        perso_name: str,
    ) -> None:
        """Init the client."""
        self.perso = perso
        self.perso_name = perso_name
