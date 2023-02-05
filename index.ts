export default class MutiplayerServerConnection {
    baseUrl: string
    socketUrl: string;
    userId?: string;
    private apiKey: string
    private socket?: WebSocket;
    private topicSubscribers: Map<string, Function>;

    constructor(baseUrl: string, apiKey: string) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
        this.socket = undefined;
        this.userId = undefined;
        this.register();
    }

    _socketConnect(socketUrl): boolean {
        this.socket = new WebSocket(socketUrl);
        this.userId = socketUrl.match(/ws\/([a-f\d-]+)/)[1]
        this.socket.onopen = () => {
            this._addMessageListener(this.socket);
        }
        return true;
    }

    _addMessageListener(socket) {
        socket.addEventListener('message', (event) => {
           console.log(event.data); 
        });
    }

    async register(): Promise<boolean> {
        const url = `http://${this.baseUrl}/register`
        const response = await fetch(url);
        return this._socketConnect(response.json()["url"]);
    }

    async unregister(): Promise<JSON> {
        const response = await fetch(`http://${this.baseUrl}/register`)
        return response.json();
    }


    subscribe(topic: string, callback: Function) {
        let data = {
                "action": "Subscribe",
                "user_id": this.userId,
                "topic": topic
            }
        this.topicSubscribers.set(topic, callback);
        return this.socket?.send(JSON.stringify(data));
    }

    unsubscribe(topic) {
        let data = {
                "action": "Unsubscribe",
                "user_id": this.userId,
                "topic": topic
            }
        return this.socket?.send(JSON.stringify(data));
    }

    set(topic: string, message: string) {
        let data = {
            "action": "Set",
            "user_id": this.userId,
            "topic": topic,
            "message": message
        }
        console.log("set", topic, message)
        return this.socket?.send(JSON.stringify(data));
    }

    unset(topic: string) {
        let data = {
            "action": "Unset",
            "user_id": this.userId,
            "topic": topic,
        }
        return this.socket?.send(JSON.stringify(data));
    }

    addToCollection(topic: string, message: string) {
        let data = {
            "action": "AddToCollection",
            "user_id": this.userId,
            "topic": topic,
            "message": message
        }
        return this.socket?.send(JSON.stringify(data));
    }

    removeFromCollection(topic: string, message: string) {
        let data = {
            "action": "RemoveFromCollection",
            "user_id": this.userId,
            "topic": topic,
            "message": message
        }
        return this.socket?.send(JSON.stringify(data));
    }
}
