import MutiplayerServerConnection from "..";

export default () => {
    let subscribe = (connection: MutiplayerServerConnection, topic: string) => {
        connection.subscribe(topic, (message) => {
            console.log(`Received message: ${message}`);
        });
    }
    let publish = (connection: MutiplayerServerConnection, topic: string, message: string) => {
        connection.set(topic, message);
    }

    let connection = new MutiplayerServerConnection("localhost:8000", "key")
    connection.register()
        .then((success) => {
            if (success) {
                console.log(`Registration success: ${connection.userId}`)
                subscribe(connection, "computers");
            }
        })
        .catch((error) => {
                console.log(`Registration error: userId: ${connection.userId}`)
        })

}
