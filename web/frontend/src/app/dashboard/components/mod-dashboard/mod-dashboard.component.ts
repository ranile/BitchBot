import { Component, OnInit } from '@angular/core';
import { User } from "../../../models/User";
import { UserService } from "../../../services/user/user.service";
import { Guild } from "../../../models/Guild";

@Component({
    selector: 'app-mod-dashboard',
    templateUrl: './mod-dashboard.component.html',
    styleUrls: ['./mod-dashboard.component.scss']
})
export class ModDashboardComponent implements OnInit {
    currentUser: User;
    selectedGuild: string | Guild;
    modIn: Guild[];

    constructor(private userService: UserService) {
    }

    ngOnInit(): void {
        this.currentUser = this.userService.currentUser
        console.log(this.currentUser.guilds)
        this.userService.modIn
            .then(it => {
                this.modIn = it
            })
            .catch(it => {
                console.error(it)
            })
    }

    onGuildSelect() {
        console.log(this.selectedGuild)
        const guild = this.currentUser.guilds.find(it => it.id == this.selectedGuild.toString())
        console.log(guild)
        this.selectedGuild = guild
    }
}
