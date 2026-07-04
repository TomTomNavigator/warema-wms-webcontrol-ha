import logging
import time
from datetime import datetime

from .wms_controller import WmsController

logger = logging.getLogger('warema_wms')


class Shade:
    def __init__(self, wms_ctrl: WmsController, room, channel,
                 time_between_cmds=0.1, num_retries=3, position=0,
                 is_moving=False, tilt=None):
        """
        Initializes a Shade entity
        :param wms_ctrl: Allows to pass in your own version of a WmsController
        :param room: Room name to which Shade belongs
        :param channel: Channel name under which Shade is reachable
        :param time_between_cmds: Time between commands if multiple commands
            are necessary. If commands are sent too quickly after each other,
            an error is returned from the webcontrol server.
        :param num_retries: Number of times to retry a failed command
        :param position:
        :param is_moving:
        :param tilt:
        """
        self.wms_ctrl = wms_ctrl
        self.room = room
        self.channel = channel
        self.time_between_cmds = time_between_cmds
        self.num_retries = num_retries
        self.position = position  # 0 for open, 100 for closed
        self.is_moving = is_moving
        self.tilt = tilt
        self.is_scene = False
        self.state_last_updated = None

    def get_room_name(self):
        return self.room.name

    def get_channel_name(self):
        return self.channel.name

    def update_shade_state(self):
        """Forces an update of the state of the shade."""
        try:
            self._try_cmd_n_times(
                lambda: self.wms_ctrl.send_rx_check_ready(
                    self.room.id, self.channel.id),
                self.num_retries)
            time.sleep(self.time_between_cmds)
            shutter_xml = self.wms_ctrl.send_rx_shade_state(
                self.room.id, self.channel.id)
            err = shutter_xml.find('errorcode')
            if err is not None and err.text in ('32', '33'):
                self.is_scene = True
                self.state_last_updated = datetime.now()
                return True
            self.is_moving = shutter_xml.find('fahrt').text != '0'
            self.position = int(shutter_xml.find('position').text) / 2
            winkel_elem = shutter_xml.find('winkel')
            if winkel_elem is not None:
                self.tilt = int(winkel_elem.text)
            self.state_last_updated = datetime.now()
            return True
        except AttributeError:
            logger.warning(
                "Couldn't update shade %s in room %s. "
                "Invalid response from server.",
                self.get_channel_name(), self.get_room_name())
            return False
        except Exception:
            logger.exception(
                "Failed to update shade %s in room %s.",
                self.get_channel_name(), self.get_room_name())
            return False

    def get_shade_state(self, force_update=False):
        """
        Returns the state that was received at the last update.
        :param force_update: Forces an update if true
        :return: Tuple of (position, tilt, is_moving, last_updated)
        """
        if force_update or self.state_last_updated is None:
            self.update_shade_state()
        return self.position, self.tilt, self.is_moving, self.state_last_updated

    def set_shade_position(self, new_position, new_tilt=None):
        """
        Sets shade to new_position and optionally new_tilt.
        :param new_position: New position of shade (0=open, 100=closed)
        :param new_tilt: New tilt angle (raw byte value), or None to keep
        """
        for _ in range(self.num_retries):
            try:
                self._try_cmd_n_times(
                    lambda: self.wms_ctrl.send_rx_check_ready(
                        self.room.id, self.channel.id),
                    self.num_retries)
                time.sleep(self.time_between_cmds)
                tilt_val = 255 if new_tilt is None else int(new_tilt)
                self.wms_ctrl.send_tx_move_shade(
                    self.room.id, self.channel.id,
                    int(new_position * 2), tilt_val)
                # Optimistically update local state
                self.position = new_position
                if new_tilt is not None:
                    self.tilt = tilt_val
                if self._verify_set_cmd_sent(new_position):
                    return True
            except Exception:
                logger.warning(
                    "Failed to set shade %s:%s, retrying...",
                    self.room.name, self.channel.name)
        logger.warning(
            "Shade %s:%s could not be set to target position %s",
            self.room.name, self.channel.name, new_position)
        return False

    def play_scene(self):
        """Activates the scene on this channel."""
        try:
            self._try_cmd_n_times(
                lambda: self.wms_ctrl.send_rx_check_ready(
                    self.room.id, self.channel.id),
                self.num_retries)
            time.sleep(self.time_between_cmds)
            self.wms_ctrl.send_tx_play_scene(self.room.id, self.channel.id)
            return True
        except Exception:
            logger.warning(
                "Scene %s:%s could not be activated",
                self.room.name, self.channel.name)
            return False

    def _try_cmd_n_times(self, cmd, n=3):
        """Try a command up to n times, returning on first success."""
        for i in range(n):
            try:
                ret = cmd()
                feedback = ret.find('feedback')
                if feedback is None or feedback.text == '1':
                    return ret
            except Exception:
                logger.warning(
                    "Command attempt %d/%d failed for %s:%s",
                    i + 1, n, self.get_room_name(), self.get_channel_name())
            time.sleep(self.time_between_cmds)
        return None

    def _verify_set_cmd_sent(self, target_position):
        time.sleep(self.time_between_cmds)
        for _ in range(self.num_retries):
            self.update_shade_state()
            if self.is_moving or self.position == target_position:
                return True
            time.sleep(self.time_between_cmds)
        return False

    @staticmethod
    def get_all_shades(wms_ctrl=None, time_between_cmds=0.1, num_retries=3):
        """
        Returns all shades in the WMS network which the WmsController
        is connected to.
        """
        wms_ctrl = WmsController() if wms_ctrl is None else wms_ctrl
        if not wms_ctrl.rooms:
            time.sleep(1)
            wms_ctrl = WmsController(wms_ctrl.target)

        shutters = []
        for room in wms_ctrl.rooms:
            for channel in room.channels:
                s = Shade(wms_ctrl, room, channel,
                          time_between_cmds, num_retries)
                s.get_shade_state()
                # The WMS WebControl hardware is very slow,
                # give it 2 seconds to recover between queries
                time.sleep(2.0)
                shutters.append(s)
        return shutters
