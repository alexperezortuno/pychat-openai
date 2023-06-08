document.addEventListener('DOMContentLoaded', () => {
    const {createApp} = Vue

    const key = "og8dfp9ghs379dflkvas5d6632uf15asd237984596w3ep2fiuhd3057so7i2b6v9uh08745y3tpo4idf9hb";

    createApp({
        data() {
            return {}
        },
        methods: {
            encrypt(data) {
                console.debug('encrypt', data);
                return CryptoJS.AES.encrypt(JSON.stringify(data), key);
            },
            login(submitEvent) {
                axios({
                    method: 'post',
                    url: '/oauth/token',
                    data: {
                        grant_type: 'password',
                        username: submitEvent.target[0].value,
                        password: submitEvent.target[1].value,
                    },
                    headers: {"Content-Type": "multipart/form-data"},
                })
                        .then((response) => {
                            res = response.data;
                            res.username = submitEvent.target[0].value;
                            sessionStorage.setItem('openai_helper', this.encrypt(res));
                            window.location.href = '/dashboard';
                        })
                        .catch((error) => {
                            console.log('Login', error);
                        })
                        .then(() => {
                            submitEvent.target[0].value = '';
                            submitEvent.target[1].value = '';
                        });
            },
        },
        mounted() {
            console.info('Login', 'app mounted');
        },
        delimiters: ['[[', ']]']
    }).mount('#app');
});
