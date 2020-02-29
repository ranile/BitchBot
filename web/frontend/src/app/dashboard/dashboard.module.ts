import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MainDashboardComponent } from './components/main-dashboard/main-dashboard.component';
import {RouterModule} from "@angular/router";
import {DashboardRoutingModule} from "./dashboard-routing.module";



@NgModule({
    declarations: [MainDashboardComponent],
    exports: [
        MainDashboardComponent
    ],
    imports: [
        CommonModule,
        RouterModule,
        DashboardRoutingModule,
    ]
})
export class DashboardModule { }
