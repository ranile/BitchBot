import * as admin from 'firebase-admin';

export class CounterService {
    private static instance: CounterService;

    private constructor() {}

    static getInstance(): CounterService {
        if (!this.instance) {
            this.instance = new CounterService()
        }

        return this.instance;
    }

    async getAllCounters() {
        const data = (await admin.firestore().collectionGroup('counters').get()).docs.map(it => it.data())
        const counters: any = {}
        data.forEach(counter => {
            counters[counter['name']] = counter['count']
        })

        return counters
    }

    async getAllCounterChannels() {
        return (await admin.firestore().collection(`/servers`).doc('quotesChannel').get()).data()
    }
}