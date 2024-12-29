# Event-Driven Network Automation with NetBox and Ansible Automation Platform

This repo contains the example code used in the upcoming Webinar: Event-Driven Network Automation with NetBox and Ansible Automation Platform, Jan 23 | 11 AM EST | 4 PM GMT. You can register for the webinar [here](https://netboxlabs.com/events/webinar-event-driven-network-automation-with-netbox-and-ansible-automation-platform/)

This joint session with NetBox Labs and Red Hat will showcase the seamless integration of NetBox as a Source of Truth with Ansible Automation Platform (AAP) and Event-Driven Ansible (EDA).
We’ll delve into NetBox’s latest features, including Branching and Change Management, and highlight new capabilities in AAP 2.5, such as the Unified UI with EDA and the interactive walkthroughs.

The live demo will feature dynamic inventory updates in AAP powered by NetBox, illustrating how event-driven automation workflows in EDA are triggered by NetBox events and data.

Use cases will include updating NTP server and VLAN configurations, as well as provisioning new devices demonstrating a streamlined, automated approach to network and infrastructure management.

All registrants will receive the recording and slides after the live webinar

## Read More in the Blog
You can also read an in-depth overview of this solution on the NetBox Labs [Blog](https://netboxlabs.com/blog/)

## Code Overview

The code is split over two directories:

### playbooks
These are the playbooks that push configuration changes out to the network devices. They are run as jobs by the Automation Execution element of Ansible Automation Platform.

### rulebooks
This code defines the rules that trigger jobs in Event Driven Ansible and configures the port that EDA listens on for NetBox event data arriving in the form of webhooks.

## Demo Environment
The demo environment consists of:

- NetBox Cloud v4.1.7 with Branching and Change Management features enabled
- Ansible Automation Platform v2.5
- 3 x Arista cEOS containerized network devices, reachable from the host running AAP
