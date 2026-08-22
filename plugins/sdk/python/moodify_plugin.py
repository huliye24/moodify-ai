#!/usr/bin/env python3
"""
Moodify Plugin SDK for Python

Enables developers to create Moodify plugins in Python.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass
class PluginManifest:
    """Plugin manifest data."""
    name: str
    version: str
    description: str = ""
    author: str = ""
    type: str = "audio-processing"
    engine: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    pricing: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> PluginManifest:
        """Load manifest from JSON file."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

    def to_file(self, path: Union[str, Path]) -> None:
        """Save manifest to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)


@dataclass
class AudioBuffer:
    """Audio buffer for processing."""
    data: bytes
    sample_rate: int
    channels: int
    format: str = "float32"

    @property
    def duration(self) -> float:
        """Calculate duration in seconds."""
        samples = len(self.data) // (4 * self.channels)  # float32 = 4 bytes
        return samples / self.sample_rate


@dataclass
class ProcessingResult:
    """Audio processing result."""
    buffer: AudioBuffer
    mrs_score: Optional[float] = None
    features: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class MoodifyPlugin:
    """
    Base class for Moodify plugins.

    Example:
        >>> class MyPlugin(MoodifyPlugin):
        ...     def process(self, buffer: AudioBuffer) -> ProcessingResult:
        ...         # Your processing logic
        ...         return ProcessingResult(buffer=buffer)
    """

    def __init__(
        self,
        manifest: Optional[PluginManifest] = None,
        api_key: Optional[str] = None,
        base_url: str = "https://api.moodify.ai"
    ):
        self.manifest = manifest
        self.api_key = api_key
        self.base_url = base_url
        self._initialized = False
        self._parameters: Dict[str, Any] = {}

    def initialize(self, sample_rate: int, buffer_size: int) -> None:
        """Initialize plugin with audio settings."""
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self._initialized = True

    def prepare(self, sample_rate: int, buffer_size: int) -> None:
        """Prepare plugin for processing (alias for initialize)."""
        self.initialize(sample_rate, buffer_size)

    def process(self, buffer: AudioBuffer) -> ProcessingResult:
        """
        Process audio buffer.

        Override this method in your plugin.

        Args:
            buffer: Input audio buffer

        Returns:
            ProcessingResult with processed audio
        """
        raise NotImplementedError("Plugin must implement process()")

    def evaluate_mrs(self, buffer: AudioBuffer) -> float:
        """
        Evaluate MRS score for audio buffer.

        Args:
            buffer: Audio buffer to evaluate

        Returns:
            MRS score (0-100)
        """
        # Future: Call Moodify API
        # For now, return placeholder
        return 70.0

    def analyze(self, buffer: AudioBuffer) -> Dict[str, Any]:
        """
        Analyze audio and return features.

        Args:
            buffer: Audio buffer to analyze

        Returns:
            Dictionary of audio features
        """
        # Future: Call Moodify API
        return {
            "duration": buffer.duration,
            "sample_rate": buffer.sample_rate,
            "channels": buffer.channels,
            "status": "placeholder"
        }

    def set_parameter(self, name: str, value: Any) -> None:
        """Set plugin parameter."""
        self._parameters[name] = value

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get plugin parameter."""
        return self._parameters.get(name, default)

    def get_parameters(self) -> Dict[str, Any]:
        """Get all parameters."""
        return self._parameters.copy()

    def load_preset(self, path: Union[str, Path]) -> None:
        """Load preset from file."""
        with open(path) as f:
            preset = json.load(f)
        self._parameters.update(preset.get("parameters", {}))

    def save_preset(self, path: Union[str, Path]) -> None:
        """Save preset to file."""
        preset = {
            "name": self.manifest.name if self.manifest else "preset",
            "version": "1.0.0",
            "parameters": self._parameters
        }
        with open(path, 'w') as f:
            json.dump(preset, f, indent=2)


class PluginHost:
    """
    Host for running Moodify plugins.

    Example:
        >>> host = PluginHost()
        >>> host.load_plugin("my_plugin.py")
        >>> result = host.process(audio_buffer)
    """

    def __init__(self):
        self._plugin: Optional[MoodifyPlugin] = None
        self._manifest: Optional[PluginManifest] = None

    def load_plugin(self, path: Union[str, Path]) -> MoodifyPlugin:
        """Load plugin from file."""
        # Load manifest
        manifest_path = Path(path).parent / "plugin.json"
        if manifest_path.exists():
            self._manifest = PluginManifest.from_file(manifest_path)

        # Import and instantiate plugin
        import importlib.util
        spec = importlib.util.spec_from_file_location("plugin", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find plugin class
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and
                issubclass(obj, MoodifyPlugin) and
                obj is not MoodifyPlugin):
                self._plugin = obj(manifest=self._manifest)
                return self._plugin

        raise ValueError("No MoodifyPlugin class found in file")

    def process(self, buffer: AudioBuffer) -> ProcessingResult:
        """Process audio through loaded plugin."""
        if self._plugin is None:
            raise RuntimeError("No plugin loaded")
        return self._plugin.process(buffer)


class PluginPackage:
    """
    Utility for packaging and validating plugins.

    Example:
        >>> packager = PluginPackage("my_plugin/")
        >>> packager.validate()
        >>> packager.build("output/")
    """

    def __init__(self, source_path: Union[str, Path]):
        self.source_path = Path(source_path)
        self.manifest_path = self.source_path / "plugin.json"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        """
        Validate plugin package.

        Returns:
            True if valid, False otherwise
        """
        self.errors = []
        self.warnings = []

        # Check manifest exists
        if not self.manifest_path.exists():
            self.errors.append("plugin.json not found")
            return False

        # Validate manifest
        try:
            manifest = PluginManifest.from_file(self.manifest_path)

            # Check required fields
            if not manifest.name:
                self.errors.append("name is required")
            if not manifest.version:
                self.errors.append("version is required")
            if not manifest.type:
                self.errors.append("type is required")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid plugin.json: {e}")
            return False

        # Check source files
        if not list(self.source_path.glob("*.py")):
            self.warnings.append("No Python files found")

        return len(self.errors) == 0

    def build(self, output_path: Union[str, Path]) -> Path:
        """
        Build plugin package.

        Args:
            output_path: Output directory

        Returns:
            Path to built package
        """
        import shutil

        output = Path(output_path)
        output.mkdir(parents=True, exist_ok=True)

        # Copy files
        for item in self.source_path.iterdir():
            if item.is_file():
                shutil.copy2(item, output)
            elif item.is_dir():
                shutil.copytree(item, output / item.name, dirs_exist_ok=True)

        return output


# Convenience exports
__all__ = [
    "MoodifyPlugin",
    "PluginManifest",
    "PluginHost",
    "PluginPackage",
    "AudioBuffer",
    "ProcessingResult",
]
