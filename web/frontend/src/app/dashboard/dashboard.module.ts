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
import { ShowAllMutesComponent } from './components/mod-dashboard/mute/show-all-mutes/show-all-mutes.component';
import { ShowMuteComponent } from './components/mod-dashboard/mute/show-mute/show-mute.component';



@NgModule({
    declarations: [MainDashboardComponent, ShowAllRemindersComponent, ShowReminderComponent, ShowAllMutesComponent, ShowMuteComponent],
    exports: [
        MainDashboardComponent,
        ShowAllMutesComponent
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
