import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from "./components/home/home.component";
import { ModDashboardComponent } from "./components/mod-dashboard/mod-dashboard.component";
import { ShowWarnsComponent } from "./components/show-warns/show-warns.component";


const routes: Routes = [
  { path: 'home', component: HomeComponent },
  { path: '', redirectTo: '/home', pathMatch: 'full' },
  { path: 'mod/dashboard', component: ModDashboardComponent },
  { path: 'mod/guild/:guild_id/warns', component: ShowWarnsComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
