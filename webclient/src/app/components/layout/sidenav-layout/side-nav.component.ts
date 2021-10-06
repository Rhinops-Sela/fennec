import {
  Component,
  OnInit,
  Input,
  Output,
  EventEmitter,
  ViewChild,
} from '@angular/core';
import { GlobalService } from 'src/app/services/global/global.service';
import { IDomain } from 'src/app/interfaces/common/IDomain';
import { Router } from '@angular/router';
import { Subject } from 'rxjs';
import {
  MatTreeFlatDataSource,
  MatTreeFlattener,
} from '@angular/material/tree';
import { FlatTreeControl } from '@angular/cdk/tree';
import { IPage } from 'src/app/interfaces/common/IPage';

interface DomainNode {
  displayName: string;
  id: string;
  children?: DomainNode[];
  repeatable: boolean;
  firstInputValue: string;
  icon?: string;
}

interface FlatNode {
  expandable: boolean;
  name: string;
  level: number;
}

@Component({
  selector: 'app-side-nav',
  templateUrl: './side-nav.component.html',
  styleUrls: ['./side-nav.component.scss'],
})
export class SideNavComponent implements OnInit {
  @ViewChild('tree') tree;
  domains: IDomain[];
  treeControl = new FlatTreeControl<FlatNode>(
    (node) => node.level,
    (node) => node.expandable
  );
  ngOnInit(): void {
    this.loadTree();
  }
  private transformer = (node: DomainNode, level: number) => {
    return {
      expandable: !!node.children && node.children.length > 0,
      name: node.displayName,
      level,
      repeatable: node.repeatable,
      firstInputValue: node.firstInputValue,
      icon: node.icon,
    };
  };

  // tslint:disable-next-line:member-ordering
  treeFlattener = new MatTreeFlattener(
    this.transformer,
    (node) => node.level,
    (node) => node.expandable,
    (node) => node.children
  );

  // tslint:disable-next-line:member-ordering
  dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

  constructor(private domainService: GlobalService, private router: Router) {
    this.domainService.refreshRequired.subscribe(() => {
      this.loadTree();
    });
  }
  hasChild = (_: number, node: FlatNode) => node.expandable;

  private loadTree() {
    this.dataSource = new MatTreeFlatDataSource(
      this.treeControl,
      this.treeFlattener
    );
    const domainsTree: DomainNode[] = [];
    this.domainService
      .getAllDomains()
      .then((result) => {
        this.domains = result;
        this.domains.forEach((domain) => {
          const pageLeafs: DomainNode[] = [];
          domain.pages.forEach((page) => {
            if (!page.icon) {
              if (page.mandatory) {
                page.icon = 'priority_high';
              } else {
                page.icon = 'check_box_outline_blank';
              }
            }
            pageLeafs.push({
              displayName: page.displayName,
              id: page.id,
              repeatable: page.repeatable || false,
              firstInputValue: page.inputs[0].value,
              icon: page.icon,
            });
          });
          domainsTree.push({
            displayName: domain.displayName,
            id: domain.id,
            children: pageLeafs,
            repeatable: false,
            firstInputValue: '',
          });
        });
        this.dataSource.data = domainsTree;
        this.tree.treeControl.expandAll();
      })
      .catch((error) => {
        console.log(error);
        this.router.navigate(['']);
      });
  }

  domainSelected(domainDisplayName: string) {
    this.domains.forEach((domain) => {
      if (domain.displayName === domainDisplayName) {
        this.domainService.onDomainChange(domain);
        this.router.navigate(['/pages']);
      }
    });
  }

  getPageName(page) {
    if (page.repeatable && page.firstInputValue) {
      return `${page.name} - ${page.firstInputValue}`;
    } else {
      return page.name;
    }
  }

  pageSelected(pageNode) {
    this.domains.find((domain) => {
      domain.pages.forEach((page: IPage) => {
        if (
          page.repeatable &&
          `${page.displayName}${page.inputs[0].value}` ===
            `${pageNode.name}${pageNode.firstInputValue}`
        ) {
          this.domainService.onPageChange(page, domain);
          this.router.navigate(['/page']);
        } else if (page.displayName === pageNode.name) {
          this.domainService.onPageChange(page, domain);
          this.router.navigate(['/page']);
        }
      });
    });
  }
}
