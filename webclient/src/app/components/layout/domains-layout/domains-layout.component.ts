import { Component, OnInit, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { IDomain } from 'src/app/interfaces/common/IDomain';
import { Router, ActivatedRoute, ParamMap } from '@angular/router';
import { GlobalService } from 'src/app/services/global/global.service';

@Component({
  selector: 'app-domain-layout',
  templateUrl: './domains-layout.component.html',
  styleUrls: ['./domains-layout.component.scss'],
})

export class DomainsLayoutComponent implements OnInit {
  public domains: IDomain[];
  @Input() selectedDomain: IDomain;
  form: FormGroup;
  constructor(public domainService: GlobalService, private router: Router, private route: ActivatedRoute) { }
  ngOnInit() {
    this.domainService.getAllDomains().then(form => {
      this.domains = form;
    }).catch(() => {
      this.router.navigate(['']);
    });
  }
  public selectDomain(domain: IDomain) {
    this.domainService.onDomainChange(domain);
    this.router.navigate(['/pages']);
  }
}
