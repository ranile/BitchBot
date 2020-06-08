import { Component, Input, OnInit } from '@angular/core';
import { BreakpointObserver } from '@angular/cdk/layout'
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
    imageDirection: {'right': boolean, left: boolean}

    constructor(private breakpointObserver: BreakpointObserver) {
    }

    ngOnInit(): void {
        this.imageDirection = {
            right: this.direction === "right",
            left: this.direction === "left"
        }
    }

    get isSmallScreen() {
        return this.breakpointObserver.isMatched('(max-width: 600px)')
    }

}
