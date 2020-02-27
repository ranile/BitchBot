import {Component, Input, OnInit} from '@angular/core';
import {Warn} from "../../models/Warn";

@Component({
  selector: 'app-show-warn',
  templateUrl: './show-warn.component.html',
  styleUrls: ['./show-warn.component.scss']
})
export class ShowWarnComponent implements OnInit {
  @Input() warn: Warn;
  constructor() { }

  ngOnInit(): void {
    console.log(this.warn)
  }

}
