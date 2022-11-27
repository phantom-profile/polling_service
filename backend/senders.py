from abc import abstractmethod
from dataclasses import dataclass
from time import time
from typing import Iterable, Protocol

from scapy.layers.inet import IP, ICMP, TCP, UDP
from scapy.packet import Packet
from scapy.sendrecv import send

from backend.utils import Loggable


class PackageSender(Protocol):
    def send_packages(self) -> None: ...

    def job_performed(self) -> bool: ...

    def logged_info(self) -> list[str]: ...


class SendersFactory(Loggable):
    TCP = 'TCP'
    UDP = 'UDP'
    ICMP = 'ICMP'
    TEST = 'TEST'
    KNOWN_PROTOCOLS = (TCP, UDP, ICMP, TEST)

    DESTINATION = 'dst.ip'
    PORT = 'dst.port'
    PACKAGES = 'packages'
    COOLDOWN = 'cooldown'
    PROTOCOL = 'service'

    def __init__(self):
        self.__products: list[PackageSender] = []
        self.__factories = self.__init_factories()

    def create_senders_from_csv(self, raw_data: Iterable):
        self.__products.clear()

        for index, line in enumerate(raw_data, start=2):
            try:
                protocol: str = line[self.PROTOCOL].upper()
            except KeyError:
                self.log_error(f'Column with name "{self.PROTOCOL}" not found!')
                break

            if protocol not in self.KNOWN_PROTOCOLS:
                self.log_error(f'ERROR: UNKNOWN SERVICE AT LINE {index}')
                break

            self.__products.append(self.__create_sender(protocol, line, index))

        return self.__products

    def __create_sender(self, protocol: str, raw_data_line: dict, index: int):
        try:
            factory_method = self.__factories.get(protocol)
            return factory_method(raw_data_line)
        except KeyError as missing_key:
            self.log_error(f'Column with name "{missing_key}" not found!')
        except ValueError:
            self.log_error(f'One of values needed to be numbers - is string! Check line {index}')

    def __test_sender(self, raw_data_line: dict) -> 'TestSender':
        return TestSender(
            destination_ip=raw_data_line[self.DESTINATION],
            cooldown_time=int(raw_data_line[self.COOLDOWN]),
            destination_port=int(raw_data_line[self.PORT]),
            packages_number=int(raw_data_line[self.PACKAGES])
        )

    def __icmp_sender(self, raw_data_line: dict) -> 'ICMPSender':
        return ICMPSender(
            destination_ip=raw_data_line[self.DESTINATION],
            cooldown_time=int(raw_data_line[self.COOLDOWN]),
            packages_number=int(raw_data_line[self.PACKAGES])
        )

    def __udp_sender(self, raw_data_line: dict) -> 'UDPSender':
        return UDPSender(
            destination_ip=raw_data_line[self.DESTINATION],
            cooldown_time=int(raw_data_line[self.COOLDOWN]),
            port=int(raw_data_line[self.PORT]),
            packages_number=int(raw_data_line[self.PACKAGES])
        )

    def __tcp_sender(self, raw_data_line: dict) -> 'TCPSender':
        return TCPSender(
            destination_ip=raw_data_line[self.DESTINATION],
            cooldown_time=int(raw_data_line[self.COOLDOWN]),
            port=int(raw_data_line[self.PORT]),
            packages_number=int(raw_data_line[self.PACKAGES])
        )

    def __init_factories(self):
        return {
            self.TEST: self.__test_sender,
            self.TCP: self.__tcp_sender,
            self.UDP: self.__udp_sender,
            self.ICMP: self.__icmp_sender,
        }


@dataclass
class BaseSender(Loggable):
    PROTOCOL = None
    SOURCE_IP = 'local'

    destination_ip: str
    cooldown_time: int
    packages_number: int

    def __post_init__(self):
        self.last_triggered = 0
        self.job_performed = False
        self.source_ip = self.SOURCE_IP

    def send_packages(self):
        if not self.time_to_send():
            self.job_performed = False
            return

        self.last_triggered = int(time())
        self.perform_sending()
        self.job_performed = True
        self.log(self.log_message)

    def time_to_send(self) -> bool:
        return time() - self.last_triggered >= self.cooldown_time

    @abstractmethod
    def perform_sending(self): ...

    @property
    @abstractmethod
    def log_message(self) -> str: ...


class ScapySender:
    source_ip: str
    SOURCE_IP: str
    destination_ip: str
    packages_number: int

    def build_ip(self):
        if self.source_ip != self.SOURCE_IP:
            return IP(dst=self.destination_ip, src=self.source_ip)
        return IP(dst=self.destination_ip)

    def send(self, protocol: Packet):
        send(self.build_ip() / protocol, count=self.packages_number, verbose=False)


@dataclass
class TestSender(BaseSender):
    destination_port: int
    protocol: str = SendersFactory.TEST

    def perform_sending(self):
        pass

    @property
    def log_message(self):
        return f'SENDING {self.packages_number} packets via {self.protocol} protocol to {self.destination_ip}'


@dataclass
class ICMPSender(BaseSender, ScapySender):
    protocol: str = SendersFactory.ICMP

    def perform_sending(self):
        protocol = ICMP()
        self.send(protocol=protocol)

    @property
    def log_message(self):
        return f'SENDING {self.packages_number} packets via {self.protocol} protocol to {self.destination_ip}'


@dataclass
class TCPSender(BaseSender, ScapySender):
    port: int
    protocol: str = SendersFactory.TCP

    def perform_sending(self):
        protocol = TCP(dport=self.port)
        self.send(protocol=protocol)

    @property
    def log_message(self):
        return f'SENDING {self.packages_number} packets ' \
               f'via {self.protocol} protocol to {self.destination_ip}:{self.port}'


@dataclass
class UDPSender(BaseSender, ScapySender):
    port: int
    protocol: str = SendersFactory.UDP

    def perform_sending(self):
        protocol = UDP(dport=self.port)
        self.send(protocol=protocol)

    @property
    def log_message(self):
        return f'SENDING {self.packages_number} packets ' \
               f'via {self.protocol} protocol to {self.destination_ip}:{self.port}'
