import {Component, Input, OnInit} from '@angular/core';
import {Warn} from "../../models/Warn";
import {User} from "../../models/User";
import {UserService} from "../../services/user/user.service";

@Component({
    selector: 'app-show-warn',
    templateUrl: './show-warn.component.html',
    styleUrls: ['./show-warn.component.scss']
})
export class ShowWarnComponent implements OnInit {
    @Input() warn: Warn;
    warnedUser: User;
    warnedBy: User;

    constructor(private userService: UserService) {
    }

    ngOnInit(): void {
        this.userService.fetchUser(this.warn.warned_user_id).then(it => {
            this.warnedUser = it
        })

        this.userService.fetchUser(this.warn.warned_by_id).then(it => {
            this.warnedBy = it
        })
        console.log(this.warn)
    }

}
