# Example
# -------
#
#   connectivity_check.py

from pyats import aetest
import re
import logging

# create a logger for this module
logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def check_topology(self,
                       testbed,
                       device1_name = 'CSR1',
                       device2_name = 'CSR2'):
        device1 = testbed.devices[device1_name]
        device2 = testbed.devices[device2_name]

        # add them to testscript parameters
        self.parent.parameters.update(device1 = device1, device2 = device2)

        # get corresponding links
        links = device1.find_links(device2)

        assert len(links) >= 1, 'require one link between device1 and device2'


    @aetest.subsection
    def establish_connections(self, steps, device1, device2):
        with steps.start('Connecting to %s' % device1.name):
            device1.connect()

        with steps.start('Connecting to %s' % device2.name):
            device2.connect()

@aetest.loop(device=('device1', 'device2'))
class PingTestcase(aetest.Testcase):

    @aetest.test.loop(destination=('192.168.1.1', '192.168.1.2'))
    def ping(self, device, destination):
        try:
            result = self.parameters[device].ping(destination)

        except Exception as e:
            self.failed('Ping {} from device {} failed with error: {}'.format(
                                destination,
                                device,
                                str(e),
                            ),
                        goto = ['exit'])
        else:
            match = re.search(r'Success rate is (?P<rate>\d+) percent', result)
            success_rate = match.group('rate')

            logger.info('Ping {} with success rate of {}%'.format(
                                        destination,
                                        success_rate,
                                    )
                               )

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect(self, steps, device1, device2):
        with steps.start('Disconnecting from %s' % device1.name):
            device1.disconnect()

        with steps.start('Disconnecting from %s' % device2.name):
            device2.disconnect()

if __name__ == '__main__':
    import argparse
    from pyats.topology import loader

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest = 'testbed',
                        type = loader.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))