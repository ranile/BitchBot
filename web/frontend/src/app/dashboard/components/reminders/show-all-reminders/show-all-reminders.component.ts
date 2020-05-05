import {Component, OnInit} from '@angular/core';
import {RemindersService} from "../../../../services/reminders/reminders.service";
import {Reminder} from "../../../../models/Reminder";

@Component({
    selector: 'app-show-all-reminders',
    templateUrl: './show-all-reminders.component.html',
    styleUrls: ['./show-all-reminders.component.scss']
})
export class ShowAllRemindersComponent implements OnInit {
    reminders: Reminder[];

    constructor(private remindersService: RemindersService) {
    }

    ngOnInit(): void {
        this.remindersService.fetchAllReminders().then(it => {
            console.log(it)
            this.reminders = it
        })
    }

}
