import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MainDashboardComponent } from './components/main-dashboard/main-dashboard.component';
import {RouterModule} from "@angular/router";
import {DashboardRoutingModule} from "./dashboard-routing.module";
import {MatButtonModule} from "@angular/material/button";
import {MatIconModule} from "@angular/material/icon";
import {MatSidenavModule} from "@angular/material/sidenav";
import {MatListModule} from "@angular/material/list";
import { ShowAllRemindersComponent } from './components/reminders/show-all-reminders/show-all-reminders.component';
import { ShowReminderComponent } from './components/reminders/show-reminder/show-reminder.component';
import {MatCardModule} from "@angular/material/card";



@NgModule({
    declarations: [MainDashboardComponent, ShowAllRemindersComponent, ShowReminderComponent],
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
        MatCardModule,
    ]
})
export class DashboardModule { }
