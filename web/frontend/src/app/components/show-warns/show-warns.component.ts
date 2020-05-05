import {Component, Input, OnDestroy, OnInit} from '@angular/core';
import {WarnsService} from "../../services/mod/warns/warns.service";
import {Warn} from "../../models/Warn";
import {ActivatedRoute} from "@angular/router";
import {Subscription} from "rxjs";
import {Guild} from "../../models/Guild";

@Component({
  selector: 'app-show-warns',
  templateUrl: './show-warns.component.html',
  styleUrls: ['./show-warns.component.scss']
})
export class ShowWarnsComponent implements OnInit {
  @Input() guild: Guild;
  warns: Warn[];

  constructor(private warnsService: WarnsService) {
  }

  ngOnInit(): void {
    this.showWarns(this.guild.id)
  }


  showWarns(guildId) {
    this.warnsService.getGuildWarns(guildId).then(warns => {
      this.warns = warns
      console.log(warns)
      console.log(this.warns)
    })
  }
}
