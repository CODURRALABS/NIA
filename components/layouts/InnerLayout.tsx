"use client";

import React, { useState } from "react";
import { Sidebar, SidebarBody, SidebarLink } from "@/components/ui/sidebar";
import { 
  LayoutDashboard, UserCog, Settings, LogOut,
  BrainCircuit, ShieldCheck, History
} from "lucide-react";
import { cn } from "@/lib/utils";

const links = [
  { label: "Sovereign Hub", href: "/hub",            icon: <BrainCircuit className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
  { label: "Dashboard",      href: "/dashboard",      icon: <LayoutDashboard className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
  { label: "Memory Bank",    href: "/memory",         icon: <History className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
  { label: "Security",       href: "/security",       icon: <ShieldCheck className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
  { label: "Personalization",href: "/personalization",icon: <UserCog className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
  { label: "Settings",       href: "/settings",       icon: <Settings className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
  { label: "Logout",         href: "#",               icon: <LogOut className="text-neutral-400 h-5 w-5 flex-shrink-0" /> },
];

export default function InnerLayout({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(true);

  return (
    <div className={cn("flex bg-black w-screen h-screen overflow-hidden border border-neutral-800")}>
      <Sidebar open={open} setOpen={setOpen}>
        <SidebarBody className="justify-between gap-10 bg-neutral-900/50 backdrop-blur-xl border-r border-white/10">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {open ? <Logo /> : <LogoIcon />}
            <div className="mt-8 flex flex-col gap-2">
              {links.map((link, idx) => (
                <SidebarLink key={idx} link={link} />
              ))}
            </div>
          </div>
          <div>
            <SidebarLink
              link={{
                label: "Admin",
                href: "#",
                icon: (
                  <div className="h-7 w-7 flex-shrink-0 rounded-full bg-gradient-to-tr from-blue-500 to-purple-600 flex items-center justify-center text-[10px] font-bold text-white">
                    AD
                  </div>
                ),
              }}
            />
          </div>
        </SidebarBody>
      </Sidebar>
      <main className="flex-1 overflow-y-auto custom-scrollbar bg-black">
        {children}
      </main>
    </div>
  );
}

const Logo = () => (
  <div className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20">
    <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
    <span className="font-medium text-black dark:text-white whitespace-pre">NIA Sovereign</span>
  </div>
);

const LogoIcon = () => (
  <div className="font-normal flex space-x-2 items-center text-sm text-black py-1 relative z-20">
    <div className="h-5 w-6 bg-black dark:bg-white rounded-br-lg rounded-tr-sm rounded-tl-lg rounded-bl-sm flex-shrink-0" />
  </div>
);
