import { Component, OnInit } from '@angular/core';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { GlobalService } from 'src/app/services/global/global.service';
import { IRefreshRequried } from 'src/app/interfaces/client/IRefreshRequried';
@Component({
  selector: 'app-toolbar-component',
  templateUrl: './toolbar-layout.component.html',
  styleUrls: ['./toolbar-layout.component.scss']
})

export class ToolbarComponent implements OnInit {
  faGithub = faGithub;
  displayNameDomain: string;
  constructor(public globalService: GlobalService) { }

  ngOnInit(): void {
    this.displayNameDomain = 'Home';
    this.globalService.refreshRequired.subscribe((result: IRefreshRequried) => {
      if (result.domainChanged) {
        const activeDomain = this.globalService.getActiveDomain();
        if (activeDomain) {
          this.displayNameDomain = activeDomain.displayName;
        } else {
          this.displayNameDomain = 'Home';
        }
      }
    });
  }





}
