import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Reminder} from "../../models/Reminder";

@Injectable({
    providedIn: 'root'
})
export class RemindersService {

    constructor(private httpClient: HttpClient) {
    }

    fetchAllReminders() {
        return this.httpClient.get<Reminder[]>('/api/reminders').toPromise()
    }
}
