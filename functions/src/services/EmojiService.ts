import * as admin from 'firebase-admin';

export class EmojiService {
    private static instance: EmojiService;

    private constructor() {}

    static getInstance(): EmojiService {
        if (!this.instance) {
            this.instance = new EmojiService()
        }

        return this.instance;
    }

    async getAllEmojis() {
        const allEmojis = (await admin.firestore().collection('emoji').get()).docs.map(it => it.data())
        return allEmojis
    }

    async getEpicEmojis() {
        const epicEmojis = (await admin.firestore().collection('epic_emojis').get()).docs.map(it => it.data())
        return epicEmojis.map(it => it.command)
    }
}