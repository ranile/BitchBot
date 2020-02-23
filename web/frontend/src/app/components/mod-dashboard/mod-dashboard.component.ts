import {Component, OnInit} from '@angular/core';
import {User} from "../../models/User";
import {UserService} from "../../services/user/user.service";
import {Guild} from "../../models/Guild";
import {Router} from "@angular/router";

@Component({
  selector: 'app-mod-dashboard',
  templateUrl: './mod-dashboard.component.html',
  styleUrls: ['./mod-dashboard.component.scss']
})
export class ModDashboardComponent implements OnInit {
  currentUser: User;
  selectedGuild: string | Guild;

  constructor(private userService: UserService, private router: Router) {
  }

  ngOnInit(): void {
    this.currentUser = this.userService.currentUser
    console.log(this.currentUser.guilds)
    // this.selectedGuild = this.currentUser.guilds[0]
  }

  onGuildSelect() {
    console.log(this.selectedGuild)
    const guild = this.currentUser.guilds.find(it => it.id == this.selectedGuild.toString())
    console.log(guild)
    this.selectedGuild = guild
  }
}
