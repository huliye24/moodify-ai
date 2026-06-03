from setuptools import setup, find_packages

setup(
    name="moodify",
    version="0.1.0",
    description="Moodify Core Engine — AI音乐情绪波场显影器",
    author="文川院 / Moodify 声音实验室",
    license="Apache-2.0",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.11.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "pyloudnorm>=0.1.0",
        "pydantic>=2.0",
        "pedalboard>=0.9.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "python-multipart>=0.0.5",
    ],
    extras_require={
        "dsp": ["pedalboard>=0.9.0"],
        "separation": ["demucs", "torch>=2.0"],
        "api": ["fastapi>=0.100.0", "uvicorn", "python-multipart"],
        "dev": ["pytest>=7.0", "httpx>=0.24.0"],
    },
    entry_points={
        "console_scripts": [
            "moodify=moodify.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
