import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './components/home/home.component';
import { HttpClientModule } from "@angular/common/http";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { MatButtonModule } from "@angular/material/button";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatCardModule } from "@angular/material/card";
import { CommandsComponent } from './components/commands/commands.component';
import { MatTableModule } from "@angular/material/table";
import { MatPaginatorModule } from "@angular/material/paginator";
import { ShowCommandComponent } from './components/commands/show-command/show-command.component';
import { MatDialogModule } from "@angular/material/dialog";
import { FeatureCardComponent } from './components/feature-card/feature-card.component';

@NgModule({
    declarations: [
        AppComponent,
        HomeComponent,
        CommandsComponent,
        ShowCommandComponent,
        FeatureCardComponent,
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        BrowserAnimationsModule,
        MatButtonModule,
        MatToolbarModule,
        MatCardModule,
        MatTableModule,
        MatPaginatorModule,
        MatDialogModule,
    ],
    providers: [],
    bootstrap: [AppComponent]
})
export class AppModule {
}
