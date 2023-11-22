from machine import UART, Pin
import utime

HOST_NAME = "GR2"
CURRENT_MESSAGE_ID = 1

BAUD_RATE = 9600
BAUD_RATE2 = 115200

uart0 = UART(0, baudrate=BAUD_RATE2)
uart1 = UART(1, baudrate=BAUD_RATE, tx=Pin(4), rx=Pin(5))

ENCODING = "UTF-8"
COMMUNICATION_ESTABLISHED = False


def process_from_server(message):
    data = message.decode(ENCODING)
    print("messageReceivedFromServer: ", data)
    data = data.strip('\n')
    messageParts = data.split("|")
    messageData = {
        "to": messageParts[0],
        "message": messageParts[1],
        "id": messageParts[2]
    }
    package = HOST_NAME + "|" + messageData["to"] + "|" + messageData["id"] + "|" + "0|" + messageData["message"]
    package + '\n'
    print("package: ", package)
    # Envio a la otra placa
    uart1.write(package.encode(ENCODING))
    
    
def process_from_router(package):
    message = package.decode(ENCODING)
    #data = data.strip("\n")
    data = ""
    for element in message:
        print(element)
        if (element == "\n"):
            break
        data = data + element
    if (len(data) == 0):
        return
    
    print("data recibida:", data)
    print(": ", data == "INIT")
    if (data == "INIT"):
        uart1.write("STARTED".encode(ENCODING))
        global COMMUNICATION_ESTABLISHED
        COMMUNICATION_ESTABLISHED = True
    elif (data == "STARTED"):
        global COMMUNICATION_ESTABLISHED
        COMMUNICATION_ESTABLISHED= True
    else:
        print("inside primer else")
        global COMMUNICATION_ESTABLISHED
        COMMUNICATION_ESTABLISHED = True
        messageParts = data.split("|")
        print(messageParts)
        messageData = {
            "emitter": messageParts[0],
            "hostReceiver": messageParts[1],
            "messageId": messageParts[2],
            "hasBeenReceived": messageParts[3],
            "message": messageParts[4]
        }
        print("messageData: ", messageData)
        if (messageData["hostReceiver"] == "GR2"):
            print("inside if hostReceiver")
            data = data + "\n"
            uart0.write(data.encode(ENCODING))
            print("messageSentToServer")
        else:
            print("inside else hostReceiver")
            # forwarding
            newData = data.strip("\n")
            newMessage = newData + "Reenvio"
            print("***NewMessage: ", newMessage)
            uart1.write(newMessage.encode(ENCODING))
            print("Se envio mensaje a router")
    

def main():
    print("Initializing router")
    iterations = 0
    while True:
        server_message = uart0.any()
        router_message = uart1.any()
        #print("servermessage")
        #print(server_message)
        #print("router message")
        #print(router_message)
        if server_message:
            print("Data received from server")
            message = uart0.read()
            process_from_server(message)
                
        if router_message != None and router_message != 0 and router_message != 1:
            print("Data received from another router")
            package = uart1.readline()
            print("message: " , package)
            process_from_router(package)
            
        if COMMUNICATION_ESTABLISHED == False:
            uart1.write("INIT\n".encode(ENCODING))
                    
        utime.sleep_ms(5000)
        #print("enviando: GR2|GR7|1|0|HelloWorld")
        #uart0.write("GR2|GR7|1|0|HelloWorld\n")
        


if __name__ == "__main__":
    main()


    
