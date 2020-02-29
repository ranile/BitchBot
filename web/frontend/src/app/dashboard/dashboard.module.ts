import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MainDashboardComponent } from './components/main-dashboard/main-dashboard.component';
import {RouterModule} from "@angular/router";
import {DashboardRoutingModule} from "./dashboard-routing.module";
import {MatButtonModule} from "@angular/material/button";
import {MatIconModule} from "@angular/material/icon";
import {MatSidenavModule} from "@angular/material/sidenav";
import {MatListModule} from "@angular/material/list";



@NgModule({
    declarations: [MainDashboardComponent],
    exports: [
        MainDashboardComponent
    ],
    imports: [
        CommonModule,
        RouterModule,
        DashboardRoutingModule,
        MatButtonModule,
        MatIconModule,
        MatSidenavModule,
        MatListModule,
    ]
})
export class DashboardModule { }
