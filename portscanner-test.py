import sys, socket, ipaddress
 
   
#function to return number of hosts in a given subnet
def numHosts(subnet):
    if "." in subnet:
        print 'the subnet is', subnet
        print ". is in subnet",subnet
        # split up the address - will return something like [255,255,255,0]   
        
        subnetlist = subnet.split(".")
        
        for subnetpart in subnetlist:
            # convert the value of the first subnet part into binary and scrap the 0b's
            # find the index of wherever the first subnetpart appears
            # assign the binary value to that index in the subnet list

            subnetlist[subnetlist.index(subnetpart)] = bin(int(subnetpart)).replace("0b","")

        cidr = str(subnetlist).count("1")

        # num of networks = 2^n - 2, expressed a cidr number. 

        # subnet mask is a count of how many 1's are in an ip. 255.255.255.255 = 32 1's
        
        # if the cidr number is between 31 and 32, then most significant bits look like this:
        #       11111111 11111111 11111111 11111111 or
        #       11111111 11111111 11111111 11111110
        
        # so, bit available for host addressing is going to be 0 or 1. 
        # otherwise, subtract 2 from the number of significant bits to account for the leading 2. 
        # that are part of the prefix.   
        
        if (int(cidr) == 32) or (int(cidr) == 31): 
            hostsCount = 2**(32-int(cidr)) 
            # hostsCount will either be 2^0 = 1 or 2^1 = 2
        else:
            hostsCount = 2**(32-int(cidr))-2
   
    return hostsCount
 
#function to generate a list with all hosts in the given subnet
def listHosts(ip, hostsCount):

    counter = 1
    hosts = []
    octs = ip.split('.')

    if hostsCount == 1:
        # add the one possible host to the list of all hosts
        hosts.append('%i.%i.%i.%i' % (int(octs[0]),int(octs[1]),int(octs[2]),int(octs[3])))
    
    elif hostsCount == 2:
        # these are the only two possible hosts
        hosts.append('%i.%i.%i.%i' % (int(octs[0]),int(octs[1]),int(octs[2]),int(octs[3])))
        hosts.append('%i.%i.%i.%i' % (int(octs[0]),int(octs[1]),int(octs[2]),int(octs[3])+1))
    else:
        while (counter <= hostsCount): 
        # here, we say 256 because the counter starts at 1.                    
            if int(octs[3]) != 256:
                octs[3] = int(octs[3])+1
        
            if (int(octs[3]) == 256) and (int(octs[2]) != 255):
                # ex. 128.1.254.256
                octs[2] = int(octs[2])+1
                octs[3], hostpart = 0, 0
                # print octs[3], hostpart = 0, 0
                # create a tuple. 128.1.255.256 becomes 128.1.255.0.0
            
            if (int(octs[2]) == 255) and (int(octs[1]) != 255):
                # 128.1.255.0.0
                octs[1] = int(octs[1])+1
                # 128.2.255.0.0
                octs[2], octs[3], hostpart = 0, 0, 0
                # print octs[2], octs[3], hostpart = 0, 0, 0
                # 128.2.0.0.0 
            
            if (int(octs[1]) == 255) and (int(octs[0]) != 255):
                # so now imagine that we've exhausted all possibilities for that second octet:
                # 128.255.0.0.0
                octs[0] = int(octs[0])+1
                # 129.255.0.0.0
                octs[1], octs[2], octs[3], hostpart  = 0, 0, 0, 0
                # print octs[1], octs[2], octs[3], hostpart
            
            hosts.append('%i.%i.%i.%i' % (int(octs[0]),int(octs[1]),int(octs[2]),int(octs[3])))

            # append these new octet groupings to the host list, and increment the counter by 1.
            counter = int(counter)+1
    print 'hosts ', hosts
    return hosts
 
#start sending icmp echo requests and list received icmp echo responds    
def pingscan(values):
    hostsCount = None
    if ("-t" in values):
        timeout = float(values[values.index('-t')+1])/float(1000)
        values.pop(values.index('-t')+1)            
        values.pop(values.index('-t'))
    else:
        timeout = 0.01
  
    if (len(values) == 2) and ("." in values[1]):
        hostsCount = numHosts(values[1])
    else:
        sys.exit(0)
               
    if hostsCount is not None:      
        print "Checking if %d hosts are alive via icmp with a timeout of %f sec" % (hostsCount, timeout)
           
        #create list with all hosts in the given subnet
        hosts = listHosts(values[1], hostsCount)
        return hosts
    
def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # google public dns
    s.connect(('8.8.8.8',80))
    ip = s.getsockname()[0]
    s.close()
    return ip
   
if __name__== "__main__":

    ip = getIP()
    subnetmask = str(ipaddress.ip_network(ip).netmask)
    values = [ip, subnetmask]
    pingscan(values)

    # print list(subnetmask.subnets())