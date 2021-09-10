from emulators.Device import Device
from emulators.Medium import Medium
from emulators.MessageStub import MessageStub


class GossipMessage(MessageStub):

    def __init__(self, sender: int, destination: int, secrets):
        super().__init__(sender, destination)
        # we use a set to keep the "secrets" here
        self.secrets = secrets

    def __str__(self):
        return f'{self.source} -> {self.destination} : {self.secrets}'


class Gossip(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])
        self._neighbour = (index + 1) % number_of_devices

    def run(self):
        def send_stuff():
            msg = GossipMessage(self.index(), self._neighbour, self._secrets)
            self.medium().send(msg)

        if self.index() == 0:
            # Lets get the party going
            send_stuff()

        while len(self._secrets) != self.number_of_devices():
            ingoing = self.medium().receive()
            if ingoing is None:
                self.medium().wait_for_next_round()
                continue

            self._secrets = self._secrets.union(ingoing.secrets)

            # Kind of hacky, but to not send it to
            # last device in chain, if the message is complete
            if not ((self._neighbour + 1) == self.number_of_devices()
               == len(ingoing.secrets)):
                send_stuff()

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')


class GossipTwoWay(Device):

    def __init__(self, index: int, number_of_devices: int, medium: Medium):
        super().__init__(index, number_of_devices, medium)
        # for this exercise we use the index as the "secret", but it could have been a new routing-table (for instance)
        # or sharing of all the public keys in a cryptographic system
        self._secrets = set([index])
        self._n1 = (index + 1) % number_of_devices
        self._n2 = (index - 1) % number_of_devices

    def run(self):
        def send_stuff(to):
            msg = GossipMessage(self.index(), to, self._secrets)
            self.medium().send(msg)

        def relay(msg: GossipMessage):
            to = self._n1 if (self._n2 == msg.source) else self._n2
            send_stuff(to)

        if self.index() == 0:
            # Lets get the party going
            send_stuff(self._n1)

        while len(self._secrets) != self.number_of_devices():
            ingoing = self.medium().receive()
            if ingoing is None:
                self.medium().wait_for_next_round()
                continue

            self._secrets = self._secrets.union(ingoing.secrets)

            if (self.index() + 1) == self.number_of_devices():
                # Uno reverse if we are last
                send_stuff(self._n2)
            elif self.index() != 0:
                relay(ingoing)

    def print_result(self):
        print(f'\tDevice {self.index()} got secrets: {self._secrets}')
