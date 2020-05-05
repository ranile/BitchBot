import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import {HttpClientModule} from "@angular/common/http";
import { NavbarComponent } from './components/navbar/navbar.component';
import { ShowWarnsComponent } from './components/show-warns/show-warns.component';
import { ModDashboardComponent } from './dashboard/components/mod-dashboard/mod-dashboard.component';
import {FormsModule} from "@angular/forms";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatButtonModule} from "@angular/material/button";
import {MatToolbarModule} from "@angular/material/toolbar";
import {MatSidenavModule} from "@angular/material/sidenav";
import {MatListModule} from "@angular/material/list";
import {MatTabsModule} from "@angular/material/tabs";
import {MatOptionModule} from "@angular/material/core";
import {MatSelectModule} from "@angular/material/select";
import { ShowWarnComponent } from './components/show-warn/show-warn.component';
import {MatCardModule} from "@angular/material/card";
import { RelativeTimePipe } from './pipes/relative-time.pipe';
import { DiscordUserPipe } from './pipes/discord-user.pipe';
import { DashboardComponent } from './dashboard/components/dashboard/dashboard.component';
import {DashboardModule} from "./dashboard/dashboard.module";
import { CommandsComponent } from './components/commands/commands.component';
import {MatTableModule} from "@angular/material/table";
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatPaginatorModule} from "@angular/material/paginator";
import {MatSortModule} from "@angular/material/sort";
import { ShowCommandComponent } from './components/commands/show-command/show-command.component';
import {MatDialogModule} from "@angular/material/dialog";

@NgModule({
    declarations: [
        AppComponent,
        HomeComponent,
        NavbarComponent,
        ShowWarnsComponent,
        ModDashboardComponent,
        DashboardComponent,
        ShowWarnComponent,
        RelativeTimePipe,
        DiscordUserPipe,
        CommandsComponent,
        ShowCommandComponent,
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        BrowserAnimationsModule,
        MatButtonModule,
        MatToolbarModule,
        MatSidenavModule,
        MatListModule,
        MatTabsModule,
        MatOptionModule,
        MatSelectModule,
        MatCardModule,
        DashboardModule,
        MatTableModule,
        MatFormFieldModule,
        MatPaginatorModule,
        MatSortModule,
        MatDialogModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule {
}
