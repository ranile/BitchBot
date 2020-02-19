import {Component, OnDestroy, OnInit} from '@angular/core';
import {WarnsService} from "../../services/mod/warns/warns.service";
import {Warn} from "../../models/Warn";
import {ActivatedRoute} from "@angular/router";
import {Subscription} from "rxjs";

@Component({
  selector: 'app-show-warns',
  templateUrl: './show-warns.component.html',
  styleUrls: ['./show-warns.component.scss']
})
export class ShowWarnsComponent implements OnInit, OnDestroy {
  warns: Warn[];
  routeMapSubscription: Subscription;

  constructor(private warnsService: WarnsService, private activatedRoute: ActivatedRoute) {
  }

  ngOnInit(): void {
    this.routeMapSubscription = this.activatedRoute.paramMap.subscribe(async (map) => {
      this.showWarns(map.get('guild_id'))
    })
  }

  ngOnDestroy(): void {
    this.routeMapSubscription.unsubscribe()
  }


  showWarns(guildId) {
    this.warnsService.getGuildWarns(guildId).then(warns => {
      this.warns = warns
      console.log(warns)
      console.log(this.warns)
    })
  }
}
