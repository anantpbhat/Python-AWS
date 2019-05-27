#!/usr/bin/env python

from boto3 import client
import argparse

class EC2:
    def __init__(self):
        parser = argparse.ArgumentParser(description="Execute specified EC2 Actions")
        parser.add_argument("--info", action="store_true", help="Display EC2 Instances Info")
        parser.add_argument("--start", action="store_true", help="Start EC2 Instance with specified ID")
        parser.add_argument("--stop", action="store_true", help="Stop EC2 Instance with specified ID")
        parser.add_argument("--listsgs", action="store_true", help="List all available Security Groups")
        parser.add_argument("--listsgrules", metavar="", help="List all rules for specified Security Group ID")
        self.args = parser.parse_args()
        self.ec2 = client('ec2')

    def ec2info(self):
        self.resp = self.ec2.describe_instances()
#       print(self.resp)
        self.EC2LST = []
        for rsv in self.resp['Reservations']:
            for instance in rsv['Instances']:
                DCT = {}
                DCT["ID"] = instance['InstanceId']
                DCT["TYP"] = instance['InstanceType']
                DCT["AZ"] = instance['Placement']['AvailabilityZone']
                DCT["SG"] = instance['SecurityGroups'][0]['GroupId']
                DCT["STATE"] = instance['State']['Name']
                DCT["VPCID"] = instance['VpcId']
                for tags in instance['Tags']:
                    if tags['Key'] == 'Name':
                        DCT["NAME"] = tags['Value']
                self.EC2LST.append(DCT)

    def displayec2(self, lst):
        Head = "\t".join(("NAME", "", "Instance ID", "", "", "Type", "", "AV Zone", "", "State", "SecGrp", "VPC"))
        print(Head)
        for i in lst:
            OUT = "\t".join((i["NAME"], i["ID"], i["TYP"], i["AZ"], i["STATE"], i["SG"], i["VPCID"]))
            print("%s" % OUT)

    def startec2(self, inp, lst):
        for i in lst:
            if (i["NAME"] == inp or i["ID"] == inp) and i["STATE"] == "stopped":
                self.ec2.start_instances(InstanceIds=[i["ID"]])
                print("Starting EC2 Instance %s ..." % i["NAME"])
            elif (i["NAME"] == inp or i["ID"] == inp) and i["STATE"] != "stopped":
                print("!!! EC2 Instance %s not in Stopped state !!!" % i["NAME"])
            else:
                pass

    def stopec2(self, inp, lst):
        for i in lst:
            if (i["NAME"] == inp or i["ID"] == inp) and i["STATE"] == "running":
                self.ec2.stop_instances(InstanceIds=[i["ID"]])
                print("Stopping EC2 Instance %s ..." % i["NAME"])
            elif (i["NAME"] == inp or i["ID"] == inp) and i["STATE"] != "running":
                print("!!! EC2 Instance %s not in Running state !!!" % i["NAME"])
            else:
                pass

    def listsgs(self):
        sg = self.ec2.describe_security_groups()
        SG_HEAD = "\t".join(("SG_NAME", "", "SG_ID"))
        print(SG_HEAD)
        self.sg_itr = sg['SecurityGroups']
        for i in self.sg_itr:
            print("%s   %s" % (i['GroupName'], i['GroupId']))

    def listsgrules(self, inp):
        for i in self.sg_itr:
            if i['GroupId'] == inp:
                print("Ingress rules for %s:-" % inp)
                for x in i['IpPermissions']:
                    fport = 0
                    if 'FromPort' in x:
                        fport = x['FromPort']
                    for B in x['IpRanges']:
                        print("%s - FromPort %d %s: %s" % (i['GroupName'], fport, x['IpProtocol'], B))
                print()
                print("Egress rules for %s:-" % inp)
                for y in i['IpPermissionsEgress']:
                    e_fport = 0
                    if 'FromPort' in y:
                        e_fport = y['FromPort']
                    for A in y['IpRanges']:
                        print("%s - FromPort %d %s: %s" % (i['GroupName'], e_fport, y['IpProtocol'], A))
                print()
            else:
                pass


if __name__ == "__main__":
    vm = EC2()
    vm.ec2info()
    if vm.args.info:
        vm.displayec2(vm.EC2LST)
    elif vm.args.start:
        vm.displayec2(vm.EC2LST)
        print("")
        startin = input("Enter Instance Name or ID to start: ")
        vm.startec2(startin, vm.EC2LST)
    elif vm.args.stop:
        vm.displayec2(vm.EC2LST)
        print("")
        stopin = input("Enter Instance Name or ID to stop: ")
        vm.stopec2(stopin, vm.EC2LST)
    elif vm.args.listsgs:
        vm.listsgs()
    elif vm.args.listsgrules:
        vm.listsgs()
        print()
        vm.listsgrules(vm.args.listsgrules)
    else:
        print("I have the Info for EC2 Instances")
