document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded with JavaScript');
    // const App = Vue.createApp({
    //     data() {
    //         return {
    //             msg: 'Hello Vue!'
    //         }
    //     },
    //     methods: {
    //         sendMessage() {
    //             console.log(this.message);
    //         }
    //     },
    // });
    //
    // App.mount('#app');
    const {createApp} = Vue
    const key = "og8dfp9ghs379dflkvas5d6632uf15asd237984596w3ep2fiuhd3057so7i2b6v9uh08745y3tpo4idf9hb";

    createApp({
        data() {
            return {
                chats: [
                    {
                        id: 'default',
                        content: "Eres una IA de ayuda para el usuario, que responde a las preguntas que se le hacen y si no sabes del tema respondes, No tengo información.",
                        message: []
                    }
                ],
            }
        },
        methods: {
            decrypt(data) {
                if (sessionStorage.getItem('openai_helper')) {
                    const session = sessionStorage.getItem('openai_helper');
                    const param = CryptoJS.AES
                            .decrypt(session, key)
                            .toString(CryptoJS.enc.Utf8);

                    if (param) {
                        return JSON.parse(param);
                    }

                    return param;
                } else {
                    window.location.href = '/auth/login';
                }
            },
            verify() {
                data = this.decrypt();
                axios({
                    method: 'post',
                    url: '/auth/verify',
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + data.access_token,
                    },
                })
                        .then((response) => {
                            console.log('verify', response);
                        })
                        .catch((error) => {
                            if (error.response.status === 401) {
                                window.location.href = '/auth/login';
                            }
                        });
            },
            sendMessage(submitEvent) {
                data = this.decrypt();
                axios({
                    method: 'get',
                    url: '/message',
                    params: {
                        message: submitEvent.target[0].value,
                        role: this.chats[0].content
                    },
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + data.access_token,
                    },
                })
                        .then((response) => {
                            console.log('message', response);
                        })
                        .catch((error) => {
                            if (error.response.status === 401) {
                                window.location.href = '/auth/login';
                            }
                        })
                        .finally(() => {
                            submitEvent.target[0].value = '';
                        });
            },
            getChats() {
                data = this.decrypt();
                axios({
                    method: 'get',
                    url: '/chat/all',
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + data.access_token,
                    },
                })
                        .then((response) => {
                            if (response.data && response.data.length > 0) {
                                this.chats = [this.chats, ...response.data];
                            }
                        })
                        .catch((error) => {
                            if (error.response.status === 401) {
                                window.location.href = '/auth/login';
                            }
                        })
                        .finally(() => {
                            submitEvent.target[0].value = '';
                        });
            },
            listenEvent() {
                document.addEventListener('message', function (e) {
                    console.log('message', e);
                });
            }
        },
        mounted() {
            console.log('mounted');
            this.getChats();
        },
        delimiters: ['[[', ']]']
    }).mount('#app');
});
