"""
Setup script for Speech Translator
==================================
This helps install and run my project easily.
"""

from setuptools import setup, find_packages

setup(
    name="speech-translator",
    version="1.0.0",
    description="Real-time Speech Translation System - My Placement Project",
    author="Naviee09",
    author_email="your.email@example.com",
    url="https://github.com/naviee09/speech-to-speech-translation",
    
    packages=find_packages(),
    
    install_requires=[
        'pyaudio>=0.2.11',
        'SpeechRecognition>=3.10.0',
        'gTTS>=2.3.0',
        'pygame>=2.5.0',
        'requests>=2.31.0',
        'numpy>=1.24.0',
        'webrtcvad>=2.0.10',
        'soundfile>=0.12.0',
    ],
    
    entry_points={
        'console_scripts': [
            'speech-translator=s2st_main_human:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
    ],
    
    python_requires='>=3.7',
    
    # My notes:
    # I tested this on Python 3.7-3.10
    # Windows and Mac both work
    # Linux should work too but I haven't tested
)
