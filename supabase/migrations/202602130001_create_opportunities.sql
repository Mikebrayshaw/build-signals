-- Build Signals: canonical opportunities table for loader + landing page preview

create extension if not exists pgcrypto;

create table if not exists public.opportunities (
    id text primary key,
    source text not null,
    source_id text not null,
    title text not null,
    description text,
    url text not null,
    external_url text,
    author text,
    score integer not null default 0,
    comments integer not null default 0,
    github_url text,
    github_data jsonb,
    topics text[],
    created_at timestamptz not null,
    fetched_at timestamptz not null default timezone('utc', now()),
    inserted_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),

    constraint opportunities_source_check
        check (source in ('hn_ask', 'hn_show', 'producthunt')),
    constraint opportunities_score_nonnegative
        check (score >= 0),
    constraint opportunities_comments_nonnegative
        check (comments >= 0),
    constraint opportunities_title_nonempty
        check (length(trim(title)) > 0),
    constraint opportunities_source_id_nonempty
        check (length(trim(source_id)) > 0),
    constraint opportunities_url_nonempty
        check (length(trim(url)) > 0),
    constraint opportunities_source_source_id_unique unique (source, source_id)
);

create index if not exists opportunities_created_at_desc_idx
    on public.opportunities (created_at desc);

create index if not exists opportunities_source_created_at_desc_idx
    on public.opportunities (source, created_at desc);

create index if not exists opportunities_score_desc_idx
    on public.opportunities (score desc);

create index if not exists opportunities_github_url_idx
    on public.opportunities (github_url)
    where github_url is not null;

create index if not exists opportunities_topics_gin_idx
    on public.opportunities using gin (topics);

create index if not exists opportunities_github_data_gin_idx
    on public.opportunities using gin (github_data jsonb_path_ops);


create or replace function public.set_opportunities_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = timezone('utc', now());
    return new;
end;
$$;

drop trigger if exists opportunities_set_updated_at on public.opportunities;
create trigger opportunities_set_updated_at
    before update on public.opportunities
    for each row
    execute function public.set_opportunities_updated_at();

alter table public.opportunities enable row level security;

-- Public landing page preview: allow read-only access with anon/authenticated keys.
drop policy if exists "public read opportunities" on public.opportunities;
create policy "public read opportunities"
    on public.opportunities
    for select
    to anon, authenticated
    using (true);

-- Service-side workflows (loader, jobs, admin) can write with service_role key.
drop policy if exists "service role write opportunities" on public.opportunities;
create policy "service role write opportunities"
    on public.opportunities
    for all
    to service_role
    using (true)
    with check (true);
