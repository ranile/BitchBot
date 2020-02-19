import { Component, OnInit } from '@angular/core';
import { User } from "../../models/User";
import { UserService } from "../../services/user/user.service";
import {Guild} from "../../models/Guild";
import {WarnsService} from "../../services/mod/warns/warns.service";
import {Warn} from "../../models/Warn";

@Component({
  selector: 'app-show-warns',
  templateUrl: './show-warns.component.html',
  styleUrls: ['./show-warns.component.scss']
})
export class ShowWarnsComponent implements OnInit {
  currentUser: User;
  warns: Warn[];
  constructor(private userService: UserService, private warnsService: WarnsService) {}

  ngOnInit(): void {
    this.currentUser = this.userService.currentUser
  }

  showWarns(guild: Guild) {
    this.warnsService.getGuildWarns(guild.id).then(warns => {
      this.warns = warns
    })
  }
}
