from lab_instruments.classes.lab_instrument import LabInstrument
import logging
import numpy as np
import abc
from typing import List, Tuple
from enum import Enum


class LightChannel(LabInstrument):
    def __init__(self, wavelengths: List[Tuple[float, float]], channel_name: Enum, log: logging._loggerClass = None, log_level = logging.INFO):
        super().__init__(log=log, log_level=log_level)
        self.channel_name = channel_name
        self._dtype_description = [('wavelength', float), ('weight', float)]
        self.spectrum = np.array(wavelengths, dtype=self._dtype_description)
        self._discrete = True
        if len(self.spectrum) > 1:
            self._discrete = False
        self.center_wavelength = self._get_center_wavelength()
        self.enabled = False
        self.intensity = 0

    @abc.abstractmethod
    def toggle_enable(self, enable: bool) -> bool:
        self.enable = enable
        return self.enabled

    @abc.abstractmethod
    def set_intensity(self, intensity: float) -> float:
        self.intensity = intensity
        return self.intensity

    def _get_center_wavelength(self):
        max_weight = np.amax(self.spectrum['weight'])
        max_weight_idx = np.where(self.spectrum['weight'] == max_weight)[0]
        self.center_wavelength = self.spectrum['wavelength'][max_weight_idx][0]
        return self.center_wavelength


class VirtualLightSource:
    def __init__(self, channels: List[LightChannel]):
        self.channels = channels

    def set_channel_intensity_by_name(self, channel_name: Enum, intensity: float):
        channel = self._get_channel_by_name(channel_name)
        set_intensity = channel.set_intensity(intensity)
        return set_intensity

    def set_channel_intensity_by_idx(self, channel_idx: int, intensity: float):
        set_intensity = self.channels[channel_idx].set_intensity(intensity)
        return set_intensity

    def get_channel_intensities(self):
        channel_intensities = [x.intensity for x in self.channels]
        return channel_intensities

    def toggle_enable_all(self, enabled: bool):
        enabled_status_list = [self.channels[x].toggle_enable(enabled) for x in range(len(self.channels))]
        return enabled_status_list

    def toggle_enable_channel_by_name(self, channel_name: Enum, enabled: bool):
        channel = self._get_channel_by_name(channel_name)
        channel_enabled = channel.toggle_enable(enabled)
        return channel_enabled

    def toggle_enable_channel_by_idx(self, channel_idx: int, enabled: bool):
        channel_enabled = self.channels[channel_idx].toggle_enable(enabled)
        return channel_enabled

    def get_lightsource_spectra(self):
        channel_spectra = [x.spectrum for x in self.channels]
        return channel_spectra

    def get_channel_spectrum_by_name(self, channel_name: Enum):
        channel = self._get_channel_by_name(channel_name)
        spectrum = channel.spectrum
        return spectrum['wavelength'], spectrum['weight']

    def get_channel_spectrum_by_idx(self, channel_idx: int):
        spectrum = self.channels[channel_idx].spectrum
        return spectrum['wavelength'], spectrum['weight']

    def _get_channel_by_name(self, channel_name: Enum):
        for channel in self.channels:
            if channel.channel_name is channel_name:
                return channel
