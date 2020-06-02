import {Component, Input, OnInit} from '@angular/core';

type ImageDirection = 'left' | 'right'

@Component({
    selector: 'app-feature-card',
    templateUrl: './feature-card.component.html',
    styleUrls: ['./feature-card.component.scss']
})
export class FeatureCardComponent implements OnInit {

    @Input() imgSource: string = "https://cdn.discordapp.com/attachments/701815317046755459/717381198975860756/unknown.png";
    @Input() title: string;
    @Input() lines: string[];
    @Input() direction: ImageDirection;
    yes = this.direction === "right"

    constructor() {
    }

    ngOnInit(): void {
        this.yes = this.direction === "right"
        console.log(this.direction, this.yes)
    }

}
