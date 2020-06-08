import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from "./components/home/home.component";
import { CommandsComponent } from "./components/commands/commands.component";


const routes: Routes = [
    { path: '', component: HomeComponent },
    { path: 'commands', component: CommandsComponent },
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
